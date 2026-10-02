"""Parse EPUB files into ChapterGuard's database-independent book model.

The parser deliberately has no knowledge of FastAPI or SQLAlchemy. It reads an
EPUB, validates the parts needed by ChapterGuard, and returns immutable Python
values that an import service can later persist in one transaction.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import posixpath
from pathlib import PurePosixPath, PureWindowsPath
import re
from typing import BinaryIO
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZIP_STORED, ZipFile, ZipInfo

from bs4 import BeautifulSoup, NavigableString, Tag


EPUB_MIMETYPE = "application/epub+zip"
XHTML_MEDIA_TYPE = "application/xhtml+xml"
NCX_MEDIA_TYPE = "application/x-dtbncx+xml"

# These limits protect the parser even before the API layer gets its own upload
# limit. Images and fonts count toward the archive total even though the parser
# does not retain them.
MAX_ARCHIVE_ENTRIES = 10_000
MAX_COMPRESSED_BYTES = 50 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 250 * 1024 * 1024
MAX_TEXT_DOCUMENT_BYTES = 10 * 1024 * 1024

FRONT_MATTER_TYPES = {
    "cover",
    "copyright-page",
    "copyrightpage",
    "dedication",
    "title-page",
    "titlepage",
    "toc",
}

BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}


class EpubParserError(ValueError):
    """Base class for errors that callers can safely translate for users."""


class InvalidEpubError(EpubParserError):
    """The input is not a structurally usable EPUB."""


class EpubLimitError(EpubParserError):
    """The EPUB exceeds a parser safety limit."""


class UnsupportedDrmError(EpubParserError):
    """The EPUB encrypts content ChapterGuard would need to read."""


class NoUsableTextError(EpubParserError):
    """The EPUB contains no usable reading-order text."""


@dataclass(frozen=True, slots=True)
class ParsedChapter:
    chapter_number: int
    title: str | None
    content: str


@dataclass(frozen=True, slots=True)
class ParsedBook:
    title: str
    author: str | None
    language: str
    file_hash: str
    chapters: tuple[ParsedChapter, ...]


@dataclass(frozen=True, slots=True)
class _ManifestItem:
    item_id: str
    member_name: str
    media_type: str
    properties: frozenset[str]


def parse_epub(
    source: str | os.PathLike[str] | BinaryIO,
    *,
    original_filename: str,
    file_hash: str,
) -> ParsedBook:
    """Return metadata and ordered plain-text sections from an EPUB.

    ``source`` may be a path or a seekable binary file object. The caller owns
    that object and remains responsible for closing or deleting it.
    """

    normalized_hash = _validate_file_hash(file_hash)

    try:
        with ZipFile(source) as archive:
            _validate_archive(archive)
            package_name = _find_package_document(archive)
            package_root = _parse_xml(
                _read_member(archive, package_name),
                description="EPUB package document",
            )
            if _local_name(package_root.tag) != "package":
                raise InvalidEpubError("The EPUB package document has the wrong root element")

            metadata = _read_metadata(package_root, original_filename)
            manifest = _read_manifest(package_root, package_name)
            spine = _read_spine(package_root, manifest)

            encrypted_members = _read_encrypted_members(archive)
            encrypted_spine_members = {
                item.member_name for item in spine if item.member_name in encrypted_members
            }
            if encrypted_spine_members:
                raise UnsupportedDrmError(
                    "The EPUB encrypts one or more reading-order documents"
                )

            toc_titles, landmark_types = _read_navigation(
                archive,
                package_root,
                package_name,
                manifest,
            )
            guide_types = _read_guide_types(package_root, package_name)

            parsed_chapters: list[ParsedChapter] = []
            for item in spine:
                if item.media_type != XHTML_MEDIA_TYPE or "nav" in item.properties:
                    continue

                raw_document = _read_member(
                    archive,
                    item.member_name,
                    maximum_size=MAX_TEXT_DOCUMENT_BYTES,
                )
                soup = BeautifulSoup(raw_document, "html.parser")

                semantics = set(guide_types.get(item.member_name, ()))
                semantics.update(landmark_types.get(item.member_name, ()))
                semantics.update(_document_semantics(soup))
                if semantics & FRONT_MATTER_TYPES:
                    continue

                title = (
                    toc_titles.get(item.member_name)
                    or _heading_title(soup)
                    or _document_title(soup)
                )
                content = _extract_plain_text(soup)
                if not content:
                    continue

                parsed_chapters.append(
                    ParsedChapter(
                        chapter_number=len(parsed_chapters) + 1,
                        title=title,
                        content=content,
                    )
                )

            if not parsed_chapters:
                raise NoUsableTextError(
                    "The EPUB contains no usable reading-order text"
                )

            return ParsedBook(
                title=metadata["title"],
                author=metadata["author"],
                language=metadata["language"],
                file_hash=normalized_hash,
                chapters=tuple(parsed_chapters),
            )
    except (EpubParserError, OSError):
        raise
    except BadZipFile as error:
        raise InvalidEpubError("The file is not a valid ZIP-based EPUB") from error
    except (KeyError, RuntimeError) as error:
        raise InvalidEpubError("The EPUB archive could not be read") from error


def _validate_file_hash(file_hash: str) -> str:
    if not isinstance(file_hash, str) or not re.fullmatch(
        r"[0-9a-fA-F]{64}", file_hash
    ):
        raise ValueError("file_hash must be a 64-character hexadecimal SHA-256 hash")
    return file_hash.lower()


def _validate_archive(archive: ZipFile) -> None:
    members = archive.infolist()
    if len(members) > MAX_ARCHIVE_ENTRIES:
        raise EpubLimitError("The EPUB contains too many archive entries")

    normalized_names: set[str] = set()
    for member in members:
        normalized_name = _normalize_member_name(member.filename)
        if normalized_name in normalized_names:
            raise InvalidEpubError("The EPUB contains duplicate archive paths")
        normalized_names.add(normalized_name)
        if member.flag_bits & 0x1:
            raise UnsupportedDrmError("Password-protected EPUB archives are unsupported")

    if sum(member.compress_size for member in members) > MAX_COMPRESSED_BYTES:
        raise EpubLimitError("The compressed EPUB is too large")
    if sum(member.file_size for member in members) > MAX_UNCOMPRESSED_BYTES:
        raise EpubLimitError("The expanded EPUB is too large")

    if not members or members[0].filename != "mimetype":
        raise InvalidEpubError("The EPUB mimetype entry must be first")
    if members[0].compress_type != ZIP_STORED:
        raise InvalidEpubError("The EPUB mimetype entry must not be compressed")

    mimetype = _read_member(archive, "mimetype").decode("ascii", errors="replace")
    if mimetype != EPUB_MIMETYPE:
        raise InvalidEpubError("The archive does not declare the EPUB media type")


def _find_package_document(archive: ZipFile) -> str:
    container_root = _parse_xml(
        _read_member(archive, "META-INF/container.xml"),
        description="EPUB container document",
    )
    if _local_name(container_root.tag) != "container":
        raise InvalidEpubError("The EPUB container has the wrong root element")
    for element in container_root.iter():
        if _local_name(element.tag) != "rootfile":
            continue
        full_path = element.attrib.get("full-path")
        if full_path:
            package_name = _normalize_member_name(unquote(full_path))
            _get_member_info(archive, package_name)
            return package_name
    raise InvalidEpubError("The EPUB does not identify a package document")


def _read_metadata(root: ET.Element, original_filename: str) -> dict[str, str | None]:
    metadata_element = _first_child(root, "metadata")
    if metadata_element is None:
        raise InvalidEpubError("The EPUB package has no metadata section")

    titles: list[str] = []
    creators: list[str] = []
    languages: list[str] = []
    for element in metadata_element.iter():
        value = _clean_label("".join(element.itertext()))
        if not value:
            continue
        name = _local_name(element.tag)
        if name == "title":
            titles.append(value)
        elif name == "creator":
            creators.append(value)
        elif name == "language":
            languages.append(value)

    title = titles[0] if titles else _filename_title(original_filename)
    author = "; ".join(dict.fromkeys(creators)) if creators else None
    language = languages[0] if languages else "und"
    return {"title": title, "author": author, "language": language}


def _read_manifest(
    root: ET.Element, package_name: str
) -> dict[str, _ManifestItem]:
    manifest_element = _first_child(root, "manifest")
    if manifest_element is None:
        raise InvalidEpubError("The EPUB package has no manifest")

    manifest: dict[str, _ManifestItem] = {}
    for element in manifest_element:
        if _local_name(element.tag) != "item":
            continue
        item_id = element.attrib.get("id", "").strip()
        href = element.attrib.get("href", "").strip()
        media_type = element.attrib.get("media-type", "").strip().lower()
        if not item_id or not href or not media_type:
            raise InvalidEpubError("An EPUB manifest item is incomplete")
        if item_id in manifest:
            raise InvalidEpubError("The EPUB manifest contains duplicate item IDs")
        manifest[item_id] = _ManifestItem(
            item_id=item_id,
            member_name=_resolve_reference(package_name, href),
            media_type=media_type,
            properties=frozenset(element.attrib.get("properties", "").split()),
        )
    return manifest


def _read_spine(
    root: ET.Element, manifest: dict[str, _ManifestItem]
) -> list[_ManifestItem]:
    spine_element = _first_child(root, "spine")
    if spine_element is None:
        raise InvalidEpubError("The EPUB package has no reading-order spine")

    spine: list[_ManifestItem] = []
    for element in spine_element:
        if _local_name(element.tag) != "itemref":
            continue
        if element.attrib.get("linear", "yes").lower() == "no":
            continue
        item_id = element.attrib.get("idref", "")
        try:
            spine.append(manifest[item_id])
        except KeyError as error:
            raise InvalidEpubError(
                "The EPUB spine refers to an unknown manifest item"
            ) from error
    return spine


def _read_navigation(
    archive: ZipFile,
    package_root: ET.Element,
    package_name: str,
    manifest: dict[str, _ManifestItem],
) -> tuple[dict[str, str], dict[str, set[str]]]:
    toc_titles: dict[str, str] = {}
    landmark_types: dict[str, set[str]] = {}

    for item in manifest.values():
        if "nav" not in item.properties:
            continue
        soup = BeautifulSoup(
            _read_member(archive, item.member_name, MAX_TEXT_DOCUMENT_BYTES),
            "html.parser",
        )
        for navigation in soup.find_all("nav"):
            navigation_types = _semantic_tokens(navigation)
            if "toc" in navigation_types:
                for link in navigation.find_all("a", href=True):
                    target = _resolve_reference(item.member_name, link["href"])
                    label = _clean_label(link.get_text(" ", strip=True))
                    if label:
                        toc_titles.setdefault(target, label)
            if "landmarks" in navigation_types:
                for link in navigation.find_all("a", href=True):
                    target = _resolve_reference(item.member_name, link["href"])
                    landmark_types.setdefault(target, set()).update(
                        _semantic_tokens(link)
                    )

    ncx_items = [item for item in manifest.values() if item.media_type == NCX_MEDIA_TYPE]
    spine_element = _first_child(package_root, "spine")
    preferred_ncx_id = spine_element.attrib.get("toc") if spine_element is not None else None
    ncx_items.sort(key=lambda item: item.item_id != preferred_ncx_id)
    for item in ncx_items:
        root = _parse_xml(
            _read_member(archive, item.member_name, MAX_TEXT_DOCUMENT_BYTES),
            description="EPUB NCX table of contents",
        )
        for nav_point in root.iter():
            if _local_name(nav_point.tag) != "navPoint":
                continue
            label = _descendant_text(nav_point, "text")
            source = _descendant_attribute(nav_point, "content", "src")
            if label and source:
                target = _resolve_reference(item.member_name, source)
                toc_titles.setdefault(target, label)

    return toc_titles, landmark_types


def _read_guide_types(
    package_root: ET.Element, package_name: str
) -> dict[str, set[str]]:
    guide_types: dict[str, set[str]] = {}
    guide = _first_child(package_root, "guide")
    if guide is None:
        return guide_types
    for reference in guide:
        if _local_name(reference.tag) != "reference":
            continue
        href = reference.attrib.get("href")
        reference_type = reference.attrib.get("type", "").lower().strip()
        if href and reference_type:
            target = _resolve_reference(package_name, href)
            guide_types.setdefault(target, set()).add(reference_type)
    return guide_types


def _read_encrypted_members(archive: ZipFile) -> set[str]:
    try:
        _get_member_info(archive, "META-INF/encryption.xml")
    except InvalidEpubError:
        return set()

    root = _parse_xml(
        _read_member(archive, "META-INF/encryption.xml"),
        description="EPUB encryption document",
    )
    encrypted_members: set[str] = set()
    for element in root.iter():
        if _local_name(element.tag) != "CipherReference":
            continue
        uri = element.attrib.get("URI")
        if uri:
            encrypted_members.add(_resolve_root_reference(uri))
    return encrypted_members


def _document_semantics(soup: BeautifulSoup) -> set[str]:
    semantics: set[str] = set()
    body = soup.body
    if body is None:
        return semantics
    semantics.update(_semantic_tokens(body))
    for child in body.find_all(["article", "main", "section"], recursive=False):
        semantics.update(_semantic_tokens(child))
    return semantics


def _semantic_tokens(tag: Tag) -> set[str]:
    values: list[str] = []
    for attribute in ("epub:type", "type", "role"):
        value = tag.get(attribute)
        if isinstance(value, str):
            values.extend(value.split())
        elif isinstance(value, list):
            values.extend(str(part) for part in value)
    tokens: set[str] = set()
    for value in values:
        token = value.lower().strip()
        if token.startswith("doc-"):
            token = token[4:]
        if token:
            tokens.add(token)
    return tokens


def _extract_plain_text(soup: BeautifulSoup) -> str:
    for element in soup.find_all(
        ["head", "nav", "script", "style", "noscript", "template", "svg"]
    ):
        element.decompose()

    root: Tag | BeautifulSoup = soup.body or soup
    pieces: list[str] = []

    def visit(node: Tag | NavigableString) -> None:
        if isinstance(node, NavigableString):
            pieces.append(str(node))
            return
        if not isinstance(node, Tag):
            return
        if node.name == "br":
            pieces.append("\n")
            return
        is_block = node.name in BLOCK_TAGS
        if is_block:
            pieces.append("\n\n")
        for child in node.children:
            visit(child)
        if is_block:
            pieces.append("\n\n")

    for child in root.children:
        visit(child)

    text = "".join(pieces).replace("\xa0", " ")
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _heading_title(soup: BeautifulSoup) -> str | None:
    ignored_ancestors = {"head", "nav", "noscript", "script", "style", "template", "svg"}
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        if any(parent.name in ignored_ancestors for parent in heading.parents):
            continue
        return _clean_label(heading.get_text(" ", strip=True)) or None
    return None


def _document_title(soup: BeautifulSoup) -> str | None:
    if soup.title is None:
        return None
    return _clean_label(soup.title.get_text(" ", strip=True)) or None


def _parse_xml(data: bytes, *, description: str) -> ET.Element:
    # EPUB 2 NCX files commonly contain a DOCTYPE. Element declarations are
    # harmless here, but custom entities are rejected to prevent entity-based
    # expansion attacks before handing the bytes to ElementTree.
    if re.search(br"<!\s*ENTITY\b", data, flags=re.IGNORECASE):
        raise InvalidEpubError(f"The {description} contains a forbidden XML entity")
    try:
        return ET.fromstring(data)
    except ET.ParseError as error:
        raise InvalidEpubError(f"The {description} is malformed") from error


def _read_member(
    archive: ZipFile,
    member_name: str,
    maximum_size: int = MAX_TEXT_DOCUMENT_BYTES,
) -> bytes:
    info = _get_member_info(archive, member_name)
    if info.file_size > maximum_size:
        raise EpubLimitError(f"EPUB entry is too large: {member_name}")
    try:
        with archive.open(info) as member:
            data = member.read(maximum_size + 1)
        if len(data) > maximum_size:
            raise EpubLimitError(f"EPUB entry is too large: {member_name}")
        return data
    except EpubLimitError:
        raise
    except (BadZipFile, OSError, RuntimeError) as error:
        raise InvalidEpubError(f"EPUB entry could not be read: {member_name}") from error


def _get_member_info(archive: ZipFile, member_name: str) -> ZipInfo:
    normalized_name = _normalize_member_name(member_name)
    try:
        return archive.getinfo(normalized_name)
    except KeyError as error:
        raise InvalidEpubError(f"The EPUB is missing a required entry: {normalized_name}") from error


def _resolve_reference(base_member: str, reference: str) -> str:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc:
        raise InvalidEpubError("The EPUB contains an external package reference")
    decoded_path = unquote(parsed.path)
    if not decoded_path:
        return _normalize_member_name(base_member)
    combined = posixpath.join(posixpath.dirname(base_member), decoded_path)
    return _normalize_member_name(combined)


def _resolve_root_reference(reference: str) -> str:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc:
        raise InvalidEpubError("The EPUB contains an external encryption reference")
    return _normalize_member_name(unquote(parsed.path))


def _normalize_member_name(name: str) -> str:
    if not name or "\\" in name or name.startswith("/"):
        raise InvalidEpubError("The EPUB contains an unsafe archive path")
    if ".." in PurePosixPath(name).parts:
        raise InvalidEpubError("The EPUB contains an unsafe archive path")
    normalized = posixpath.normpath(name)
    parts = PurePosixPath(normalized).parts
    if normalized in {"", "."} or ".." in parts:
        raise InvalidEpubError("The EPUB contains an unsafe archive path")
    return normalized


def _first_child(root: ET.Element, name: str) -> ET.Element | None:
    for child in root:
        if _local_name(child.tag) == name:
            return child
    return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _descendant_text(root: ET.Element, name: str) -> str | None:
    for element in root.iter():
        if _local_name(element.tag) == name:
            value = _clean_label("".join(element.itertext()))
            return value or None
    return None


def _descendant_attribute(
    root: ET.Element, name: str, attribute: str
) -> str | None:
    for element in root.iter():
        if _local_name(element.tag) == name:
            return element.attrib.get(attribute)
    return None


def _clean_label(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _filename_title(filename: str) -> str:
    # Handle either kind of path separator without trusting the client-supplied
    # filename as a filesystem path.
    basename = PureWindowsPath(filename).name
    basename = PurePosixPath(basename).name
    title = PurePosixPath(basename).stem.strip()
    return title or "Untitled"

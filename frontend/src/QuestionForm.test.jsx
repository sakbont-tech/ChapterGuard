import React from 'react';
import {
  cleanup,
  render,
  screen,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';
import '@testing-library/jest-dom/vitest';

import QuestionForm from './QuestionForm';

const BOOKS_URL = 'http://localhost:8000/books';
const ASK_URL = 'http://localhost:8000/ask';
const mockBooks = [
  { book_id: 'dune', title: 'Dune', total_chapters: 5 },
];

describe('QuestionForm', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  function mockBooksFetch() {
    fetch.mockImplementation((url) => {
      if (url === BOOKS_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue(mockBooks),
        });
      }

      return Promise.reject(new Error(`Unhandled fetch URL: ${url}`));
    });
  }

  async function fillForm(user) {
    await screen.findByRole('option', { name: 'Dune' });

    await user.selectOptions(
      screen.getByLabelText('Book title'),
      'dune',
    );

    await user.selectOptions(
      screen.getByLabelText('Current chapter'),
      '5',
    );

    await user.type(
      screen.getByLabelText('Question'),
      'Who is Paul?',
    );
  }

  it('renders all inputs', () => {
    mockBooksFetch();

    render(<QuestionForm />);

    expect(
      screen.getByLabelText('Book title'),
    ).toBeInTheDocument();

    expect(
      screen.getByLabelText('Current chapter'),
    ).toBeInTheDocument();

    expect(
      screen.getByLabelText('Question'),
    ).toBeInTheDocument();

    expect(
      screen.getByRole('button', { name: 'Submit' }),
    ).toBeInTheDocument();
  });

  it('allows the user to fill in the form', async () => {
    const user = userEvent.setup();
    mockBooksFetch();

    render(<QuestionForm />);

    await fillForm(user);

    expect(
      screen.getByLabelText('Book title'),
    ).toHaveValue('dune');

    expect(
      screen.getByLabelText('Current chapter'),
    ).toHaveValue('5');

    expect(
      screen.getByLabelText('Question'),
    ).toHaveValue('Who is Paul?');
  });

  it('does not display an answer before submission', () => {
    mockBooksFetch();

    render(<QuestionForm />);

    expect(
      screen.queryByText(
        'This is a spoiler free response!',
      ),
    ).not.toBeInTheDocument();
  });

  it('shows loading and disables the button while waiting', async () => {
    const user = userEvent.setup();
    mockBooksFetch();

    fetch.mockImplementation((url) => {
      if (url === BOOKS_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue(mockBooks),
        });
      }

      if (url === ASK_URL) {
        return new Promise(() => {});
      }

      return Promise.reject(new Error(`Unhandled fetch URL: ${url}`));
    });

    render(<QuestionForm />);

    await fillForm(user);

    const submitButton = screen.getByRole('button', {
      name: 'Submit',
    });

    await user.click(submitButton);

    expect(
      screen.getByText('Loading answer...'),
    ).toBeInTheDocument();

    expect(submitButton).toBeDisabled();
  });

  it('submits the correct request and displays the response', async () => {
    const user = userEvent.setup();
    mockBooksFetch();

    fetch.mockImplementation((url) => {
      if (url === BOOKS_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue(mockBooks),
        });
      }

      if (url === ASK_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue({
            answer: 'This is a spoiler free response!',
          }),
        });
      }

      return Promise.reject(new Error(`Unhandled fetch URL: ${url}`));
    });

    render(<QuestionForm />);

    await fillForm(user);

    await user.click(
      screen.getByRole('button', { name: 'Submit' }),
    );

    expect(fetch).toHaveBeenCalledWith(
      ASK_URL,
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          book_id: 'dune',
          current_chapter: 5,
          question: 'Who is Paul?',
        }),
      }),
    );

    expect(
      await screen.findByText(
        'This is a spoiler free response!',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByRole('button', { name: 'Submit' }),
    ).toBeEnabled();
  });

  it('displays the submitted reading status after success', async () => {
    const user = userEvent.setup();
    mockBooksFetch();

    fetch.mockImplementation((url) => {
      if (url === BOOKS_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue(mockBooks),
        });
      }

      if (url === ASK_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue({
            answer: 'This is a spoiler free response!',
          }),
        });
      }

      return Promise.reject(new Error(`Unhandled fetch URL: ${url}`));
    });

    render(<QuestionForm />);

    await fillForm(user);

    await user.click(
      screen.getByRole('button', { name: 'Submit' }),
    );

    expect(
      await screen.findByText('Book Title: Dune'),
    ).toBeInTheDocument();

    expect(
      screen.getByText('Current Chapter: 5'),
    ).toBeInTheDocument();
  });

  it('displays an HTTP error', async () => {
    const user = userEvent.setup();
    vi.spyOn(console, 'log').mockImplementation(() => {});
    mockBooksFetch();

    fetch.mockImplementation((url) => {
      if (url === BOOKS_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue(mockBooks),
        });
      }

      if (url === ASK_URL) {
        return Promise.resolve({
          ok: false,
          status: 500,
        });
      }

      return Promise.reject(new Error(`Unhandled fetch URL: ${url}`));
    });

    render(<QuestionForm />);

    await fillForm(user);

    await user.click(
      screen.getByRole('button', { name: 'Submit' }),
    );

    expect(
      await screen.findByText(
        'HTTP error! Status: 500',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByRole('button', { name: 'Submit' }),
    ).toBeEnabled();
  });

  it('displays a network error', async () => {
    const user = userEvent.setup();
    vi.spyOn(console, 'log').mockImplementation(() => {});
    mockBooksFetch();

    fetch.mockImplementation((url) => {
      if (url === BOOKS_URL) {
        return Promise.resolve({
          ok: true,
          json: vi.fn().mockResolvedValue(mockBooks),
        });
      }

      if (url === ASK_URL) {
        return Promise.reject(new Error('Network error'));
      }

      return Promise.reject(new Error(`Unhandled fetch URL: ${url}`));
    });

    render(<QuestionForm />);

    await fillForm(user);

    await user.click(
      screen.getByRole('button', { name: 'Submit' }),
    );

    expect(
      await screen.findByText('Network error'),
    ).toBeInTheDocument();

    expect(
      screen.getByRole('button', { name: 'Submit' }),
    ).toBeEnabled();
  });
});

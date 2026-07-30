import React from 'react';
import {render, screen, cleanup} from '@testing-library/react';
import ReadingStatus from './ReadingStatus';
import {describe, it, expect, afterEach} from 'vitest';
import "@testing-library/jest-dom/vitest"

describe("Reading status", () => {
    
    it("Displays the book title and current chapter", () => {
        render(<ReadingStatus bookTitle={"A Game of Thrones"} currentChapter={15}/>);
        expect(screen.getByText("Book Title: A Game of Thrones")).toBeInTheDocument();
        expect(screen.getByText("Current Chapter: 15")).toBeInTheDocument();
    });
});
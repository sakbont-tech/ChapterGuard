import React from 'react';
import {render, screen} from '@testing-library/react';
import QuestionForm from './QuestionForm';
import {describe, it, expect} from 'vitest';
import "@testing-library/jest-dom/vitest"
import userEvent from '@testing-library/user-event';


describe("Question form", () => {
    
    it("renders all inputs",  () => {
        render(<QuestionForm/>);
        expect(screen.getByLabelText("Book title")).toBeInTheDocument();
        expect(screen.getByLabelText("Current chapter")).toBeInTheDocument();
        expect(screen.getByLabelText("Question")).toBeInTheDocument();
    });

    it('allows the user to fill in the form', async () => {
        const user = userEvent.setup();

        render(<QuestionForm />);

        const titleInput = screen.getByLabelText('Book title');
        const chapterInput = screen.getByLabelText('Current chapter');
        const questionInput = screen.getByLabelText('Question');

        await user.type(titleInput, 'Dune');
        await user.type(chapterInput, '5');
        await user.type(questionInput, 'Who is Paul?');

        expect(titleInput).toHaveValue('Dune');
        expect(chapterInput).toHaveValue(5);
        expect(questionInput).toHaveValue('Who is Paul?');
    });
});
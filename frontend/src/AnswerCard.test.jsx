import React from 'react';
import {render, screen} from '@testing-library/react';
import AnswerCard from './AnswerCard';
import {describe, it, expect} from 'vitest';
import "@testing-library/jest-dom/vitest"

describe("Answer", () => {
    
    it("renders an answer",  () => {
        render(<AnswerCard answer={"This is a spoiler free answer"}/>);
        const text = screen.getByText("This is a spoiler free answer");
        expect(text).toBeInTheDocument();
    });

});
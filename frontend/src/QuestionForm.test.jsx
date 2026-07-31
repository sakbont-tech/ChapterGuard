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

describe('QuestionForm', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  async function fillForm(user) {
    await user.type(
      screen.getByLabelText('Book title'),
      'Dune',
    );

    await user.type(
      screen.getByLabelText('Current chapter'),
      '5',
    );

    await user.type(
      screen.getByLabelText('Question'),
      'Who is Paul?',
    );
  }

  it('renders all inputs', () => {
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

    render(<QuestionForm />);

    await fillForm(user);

    expect(
      screen.getByLabelText('Book title'),
    ).toHaveValue('Dune');

    expect(
      screen.getByLabelText('Current chapter'),
    ).toHaveValue(5);

    expect(
      screen.getByLabelText('Question'),
    ).toHaveValue('Who is Paul?');
  });

  it('does not display an answer before submission', () => {
    render(<QuestionForm />);

    expect(
      screen.queryByText(
        'This is a spoiler free response!',
      ),
    ).not.toBeInTheDocument();
  });

  it('shows loading and disables the button while waiting', async () => {
    const user = userEvent.setup();

    // This Promise never finishes, so the component stays loading.
    fetch.mockReturnValue(new Promise(() => {}));

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

    fetch.mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        response: 'This is a spoiler free response!',
      }),
    });

    render(<QuestionForm />);

    await fillForm(user);

    await user.click(
      screen.getByRole('button', { name: 'Submit' }),
    );

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/ask',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Dune',
          chapter: 5,
          question: 'Who is Paul?',
        }),
      },
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

    fetch.mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        response: 'This is a spoiler free response!',
      }),
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

    fetch.mockResolvedValue({
      ok: false,
      status: 500,
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

    fetch.mockRejectedValue(
      new Error('Network error'),
    );

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
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders SnoringCare brand', () => {
  render(<App />);
  const brandElements = screen.getAllByText(/SnoringCare/i);
  expect(brandElements.length).toBeGreaterThan(0);
});

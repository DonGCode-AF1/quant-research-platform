import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import App from "./App";

globalThis.fetch = vi.fn().mockResolvedValue({ok: true, json: async () => []}) as unknown as typeof fetch;

test("renders the research navigation", async () => {
  render(<QueryClientProvider client={new QueryClient()}><App /></QueryClientProvider>);
  expect(screen.getByText("策略图谱")).toBeInTheDocument();
  expect(screen.getByText("回测构建")).toBeInTheDocument();
});

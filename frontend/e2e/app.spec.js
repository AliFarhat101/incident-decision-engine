import { test, expect } from "@playwright/test";

test("app loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Incident Decision Engine")).toBeVisible();
});

test("predict flow returns a decision", async ({ page }) => {
  await page.goto("/");

  // Use a demo sample button if present
  const sampleBtn = page.getByRole("button", { name: "DB error" });
  await sampleBtn.click();

  const analyzeBtn = page.getByRole("button", { name: /Analyze/i });
  await expect(analyzeBtn).toBeEnabled();

  await analyzeBtn.click();

  // Decision section should show badges
  await expect(page.getByText(/Type:/)).toBeVisible();
  await expect(page.getByText(/Severity:/)).toBeVisible();
  await expect(page.getByText(/Team:/)).toBeVisible();
});

test("empty log disables Analyze", async ({ page }) => {
  await page.goto("/");

  // Clear textarea (if any)
  const textarea = page.locator("textarea");
  await textarea.fill("");

  const analyzeBtn = page.getByRole("button", { name: /Analyze/i });
  await expect(analyzeBtn).toBeDisabled();
});

import { test, expect } from '@playwright/test';

const modelsPayload = {
  models: [
    { name: 'qwen3:8b', modified_at: '2024-01-01T00:00:00Z', size: 0 },
    { name: 'llama3:8b', modified_at: '2024-01-01T00:00:00Z', size: 0 },
    { name: 'gemma3:1b', modified_at: '2024-01-01T00:00:00Z', size: 0 },
  ],
};

test.beforeEach(async ({ page }) => {
  await page.route('**/api/models', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(modelsPayload),
    });
  });
});

test('shows onboarding suggestions and applies them to the composer', async ({ page }) => {
  await page.goto('/');

  const composer = page.getByPlaceholder('Type your message...');
  await expect(composer).toBeEnabled();

  await expect(page.getByRole('heading', { name: 'Start a Conversation' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Tell me a story' })).toBeVisible();

  await page.getByRole('button', { name: 'Tell me a story' }).click();
  await expect(composer).toHaveValue('Tell me a story');
});

test('creates, renames, and deletes conversations from the sidebar', async ({ page }) => {
  await page.goto('/');

  const composer = page.getByPlaceholder('Type your message...');
  await expect(composer).toBeEnabled();

  await page.getByRole('button', { name: 'New Conversation' }).click();
  await expect(page.getByText('2 conversations')).toBeVisible();

  await page.getByTitle('Rename').first().click();
  const renameInput = page.locator('input[type="text"]').first();
  await renameInput.fill('Project planning');
  await renameInput.press('Enter');
  await expect(page.getByText('Project planning')).toBeVisible();

  await page.evaluate(() => {
    window.confirm = () => true;
  });

  await page.getByTitle('Delete').nth(1).click();
  await expect(page.getByText('1 conversation')).toBeVisible();
  await expect(page.getByText('Project planning')).toBeVisible();
});

test('streams assistant responses in simple mode', async ({ page }) => {
  await page.route('**/api/chat', async (route) => {
    const payload = route.request().postDataJSON();
    expect(payload.model).toBe('gemma3:1b');
    const body = [
      JSON.stringify({ message: { content: 'Hello from Playwright' } }),
      JSON.stringify({ message: { content: '! Have a great day.' } }),
      JSON.stringify({ done: true }),
    ].join('\n');

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body,
    });
  });

  await page.goto('/');

  const composer = page.getByPlaceholder('Type your message...');
  await expect(composer).toBeEnabled();

  await page.getByRole('combobox').selectOption('gemma3:1b');
  await composer.fill('Hi there');

  const sendButton = page.getByRole('button', { name: 'Send' });
  await sendButton.click();
  await expect(sendButton).toBeDisabled();

  await expect(page.getByText('Hello from Playwright! Have a great day.')).toBeVisible();
  await expect(composer).toHaveAttribute('placeholder', 'Type your message...');
  await composer.fill('Thanks!');
  await expect(sendButton).toBeEnabled();
});

test('prevents agent mode requests when model lacks tool support', async ({ page }) => {
  let agentRequestCount = 0;
  await page.route('**/api/agent/chat', async (route) => {
    agentRequestCount += 1;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '',
    });
  });

  await page.goto('/');

  const composer = page.getByPlaceholder('Type your message...');
  await expect(composer).toBeEnabled();

  await page.getByRole('combobox').selectOption('llama3:8b');
  await page.getByRole('button', { name: 'Agent Mode' }).click();

  await composer.fill('Plan a trip to Tokyo');
  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByText('⚠️ Model "llama3:8b" doesn\'t support tools. Please use: qwen3:8b')).toBeVisible();
  expect(agentRequestCount).toBe(0);
});

test('shows tool usage details after an agent response', async ({ page }) => {
  await page.route('**/api/agent/chat', async (route) => {
    const events = [
      JSON.stringify({ type: 'tool_call', tool: 'calculator', args: { expression: '2+2' } }),
      JSON.stringify({ type: 'tool_result', tool: 'calculator', result: '4' }),
      JSON.stringify({ type: 'message', content: 'The result is 4.' }),
      JSON.stringify({ type: 'done' }),
    ].join('\n');

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: events,
    });
  });

  await page.goto('/');

  const composer = page.getByPlaceholder('Type your message...');
  await expect(composer).toBeEnabled();

  await page.getByRole('button', { name: 'Agent Mode' }).click();
  await expect(page.getByText('Agent Active')).toBeVisible();

  await composer.fill('What is 2 + 2?');
  await page.getByRole('button', { name: 'Send' }).click();

  await expect(page.getByText('The result is 4.')).toBeVisible();
  await expect(page.getByText('Used 1 tool')).toBeVisible();
  await expect(page.getByText('calculator')).toBeVisible();
});

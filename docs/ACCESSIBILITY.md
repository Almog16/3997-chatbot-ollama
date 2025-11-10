# Accessibility Statement (A11y)

## Our Commitment

This project is committed to ensuring a high-quality experience for all users, including those with disabilities. We believe that a local-first, developer-oriented tool should still be built on a foundation of inclusivity. This document outlines our current accessibility features, our known shortcomings, and our plan for improvement.

## Current State

We have implemented several foundational accessibility features:

1.  **Keyboard Navigation:** The application is navigable using a keyboard. Users can:
    *   `Tab` to move between interactive elements (sidebar, buttons, chat input).
    *   `Enter` to activate buttons and send messages.
    *   `Shift + Enter` to create a new line in the chat input.
2.  **Semantic HTML:** We have used semantic HTML elements like `<button>`, `<input>`, and `<textarea>` where appropriate to provide inherent accessibility.
3.  **Readable Layout:** The interface uses a clean, hierarchical layout that is easy to understand and visually follow.

## Known Gaps and Future Improvements

We recognize that accessibility is a journey, not a destination. Here are the key areas we have identified for improvement to better support users of assistive technologies like screen readers.

### 1. Lack of ARIA Attributes for Dynamic Content

The UI currently lacks specific ARIA (Accessible Rich Internet Applications) attributes that provide crucial context for screen readers.

*   **Problem:** Screen readers may not announce when the agent starts or finishes a tool call, or when the model status changes. Icon-only buttons (like "Delete Conversation") are not descriptive.
*   **Solution:**
    *   Add `aria-label` to all icon-only buttons to describe their function (e.g., `aria-label="Delete conversation"`).
    *   Implement `aria-live` regions for status indicators (e.g., "Processing...", "Agent Active") so that changes are announced automatically.
    *   Assign ARIA `role` attributes to different sections of the application (e.g., `role="log"` for the message list, `role="navigation"` for the sidebar).

### 2. Suboptimal Focus Management

The browser's default focus behavior is used, which can be improved for a more intuitive workflow.

*   **Problem:** After deleting a conversation, the focus is lost or moves to an unpredictable location.
*   **Solution:**
    *   After deleting a conversation, programmatically move the focus to the next logical element, such as the next conversation in the list or the "New Conversation" button.
    *   When a new conversation is created, ensure the focus automatically shifts to the chat input area.

### 3. Formal Color Contrast Audit

While we have aimed for good contrast, a formal audit has not been performed.

*   **Problem:** Some text or UI elements may not meet the WCAG (Web Content Accessibility Guidelines) AA or AAA contrast ratios, making them difficult to read for users with low vision.
*   **Solution:** Use browser developer tools (like Lighthouse) to audit the entire application and adjust any colors that fail to meet the required contrast ratios.

## How to Provide Feedback

We welcome your feedback on the accessibility of this application. If you encounter any barriers or have suggestions for improvement, please open an issue on the project's GitHub repository.

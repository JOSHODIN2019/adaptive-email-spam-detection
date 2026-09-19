# Claude Code Instructions

## Core Principle

You are not finished when the code compiles or the page loads.
Your task is to continuously verify both the visual implementation and functionality until they closely match the provided reference and work without errors.

---

## Visual Verification Loop

After every implementation:

1. Run the application.
2. Capture a fresh screenshot of the current result.
3. Compare the screenshot against the provided reference image.
4. Identify every visual difference, including:
   - Layout
   - Spacing
   - Alignment
   - Typography
   - Font sizes
   - Font weights
   - Colors
   - Shadows
   - Borders
   - Radius values
   - Padding and margins
   - Component sizing
   - Responsive behavior
   - Hover states
   - Animations
   - Overall visual hierarchy
5. Create a list of all detected differences.
6. Fix the differences.
7. Generate a new screenshot.
8. Compare again.
9. Repeat this process until the implementation is visually indistinguishable from the reference image.

Do not stop after one comparison cycle.

Continue iterating until:
- No meaningful visual differences remain.
- Spacing and proportions match.
- Components appear in the correct positions.
- The overall UI closely matches the reference design.

Be extremely critical during comparison. Assume the design is incorrect until proven otherwise.

---

## Functional Verification Loop

After implementing any feature:

- Test every user flow.
- Test every button.
- Test every link.
- Test every form.
- Test every modal.
- Test every dropdown.
- Test every navigation path.
- Test every API call.
- Test every loading state.
- Test every error state.
- Test responsiveness on mobile, tablet, and desktop.
- Check browser console for errors.
- Check network requests for failures.
- Check accessibility issues where possible.

If any issue is found:
1. Identify root cause.
2. Fix the issue.
3. Rebuild the application if required.
4. Retest the affected functionality.
5. Retest related functionality to ensure no regressions.
6. Repeat until all tests pass.

Never assume functionality works simply because the UI renders.

---

## Completion Criteria

You may only consider the task complete when:

### Visual Quality
- The latest screenshot closely matches the reference image.
- No major visual inconsistencies remain.
- Responsive layouts behave correctly.

### Functional Quality
- All interactive elements work correctly.
- No console errors exist.
- No failed network requests exist.
- All intended user flows complete successfully.
- Edge cases have been tested.
- Regression checks pass.

Before declaring completion, provide:
- Final comparison summary.
- List of fixes performed.
- Remaining differences (if any).
- Functional test results.
- Confirmation that both visual and functional verification loops were completed multiple times.

Do not stop at implementation. Implement → Verify → Fix → Retest → Repeat until quality standards are met.

---

## Architecture & Documentation Standards

Act as a senior software architect, full-stack engineer, QA engineer, and technical writer.

### Before writing code:
- Design the complete system architecture.
- Create a project structure.
- List all technologies required.
- Explain why each technology is needed.
- Create documentation files for architecture, APIs, database, components, and project mapping.

### During development:
- Build features module by module.
- Keep code organized according to the architecture.
- Update documentation after every major change.
- Maintain a project map showing where every file lives and what it does.
- Explain every new technology introduced.

### After implementation:
- Perform visual verification using screenshots.
- Compare against the provided reference.
- Fix differences and repeat.
- Perform functional testing.
- Fix bugs and repeat.
- Continue until visual and functional quality standards are met.

Never sacrifice architecture for speed. Build quickly, but maintain a clean, scalable, documented codebase at all times.

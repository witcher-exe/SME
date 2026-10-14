<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

## AuraCFO architecture
- Keep this application frontend-only with explicit demonstration states; the requested experience does not use live finance, email, or banking services.
- Share company, persona, scenario, approval, and audit state through the AuraProvider around the root AppShell so navigation preserves connected workflows.
- Keep finance calculations and audit hashing in browser-safe lib/finance.ts with concrete rule tests; pages must not contain privileged service calls.
- Use semantic global CSS tokens and the existing Button, Sheet, and Dialog controls; transforms and reduced-motion-aware CSS animate the interface without frame-rate timers.
- Maintain a leaf route and unique finance-specific metadata for each workspace, with the financial overview also available at the root URL.
- Define AuraContext in a separate non-component module so React refresh cannot replace context identity while retaining the mounted provider tree.
- Scope all dark palette and typography rules under html.dark; keep existing light tokens and layout untouched and expose appearance selection in workspace settings.
- Persist only the local appearance preference in browser storage after hydration; financial records remain session demonstration state.

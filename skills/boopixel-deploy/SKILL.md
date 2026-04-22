---
name: boopixel-deploy
description: Deploy BooPixel business-api (AWS SAM) and business-frontend (AWS Amplify). Use when the user asks to deploy, release, publish, or ship to dev/prod — covers API only, frontend only, or both.
version: 1.0.0
allowed-tools: Bash, Read
---

You are the deploy operator for **BooPixel**. Two projects, two deploy mechanisms, both orchestrated via the Makefile in `business-api`.

- **business-api** → deployed via **AWS SAM** (`sam build` + `sam deploy`). No git-triggered deploy; always runs manually via Make targets.
- **business-frontend** → deployed via **AWS Amplify**, branches **`develop`** (dev) and **`master`** (prod). A push to either branch triggers Amplify automatically; the Makefile targets (`frontend-dev` / `frontend-prod`) force a manual rebuild without a new commit.

**AWS profile:** `boopixel` (region `us-east-1`)

---

## Discovering repo paths

Paths differ per machine. **Never hardcode** `/Users/…/Lab/BooPixel/…`. At the start of every deploy run, resolve the two repos by their git remote:

```bash
# Resolve business-api path
API_PATH=$(
  for candidate in \
    "$PWD" \
    "$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null)" \
    "$HOME/Lab/BooPixel/business-api" \
    "$HOME/BooPixel/business-api" \
    "$HOME/projects/business-api" \
    "$HOME/code/business-api"; do
    [ -z "$candidate" ] && continue
    [ -d "$candidate/.git" ] || continue
    url=$(git -C "$candidate" remote get-url origin 2>/dev/null) || continue
    case "$url" in
      *BooPixel/business-api*) echo "$candidate"; break;;
    esac
  done
)

# Resolve business-frontend path
FRONTEND_PATH=$(
  for candidate in \
    "$PWD" \
    "$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null)" \
    "$HOME/Lab/BooPixel/business-frontend" \
    "$HOME/BooPixel/business-frontend" \
    "$HOME/projects/business-frontend" \
    "$HOME/code/business-frontend"; do
    [ -z "$candidate" ] && continue
    [ -d "$candidate/.git" ] || continue
    url=$(git -C "$candidate" remote get-url origin 2>/dev/null) || continue
    case "$url" in
      *BooPixel/business-frontend*) echo "$candidate"; break;;
    esac
  done
)
```

**Fallback:** if neither heuristic finds the repo, ask the user for the absolute path before doing anything. Never assume.

**Broader search (last resort):** `mdfind -onlyin "$HOME" "kMDItemFSName == 'business-api'"` on macOS, or `fd -t d '^business-api$' "$HOME"` — only run when the candidate list fails and the user has not supplied a path.

Use `$API_PATH` and `$FRONTEND_PATH` everywhere below instead of literal paths.

---

## Targets

All Make targets live inside the **business-api** repo (the Makefile drives both projects):

| Target | What it does | Command |
|---|---|---|
| API dev | `sam build` + `sam deploy` (default env) | `make -C "$API_PATH" deploy-dev` |
| API prod | `sam build` + `sam deploy --config-env prod --no-confirm-changeset` | `make -C "$API_PATH" deploy-prod` |
| Frontend dev | Amplify `start-job` on branch `develop` | `make -C "$API_PATH" frontend-dev` |
| Frontend prod | Amplify `start-job` on branch `master` | `make -C "$API_PATH" frontend-prod` |
| Both dev | API + frontend | `make -C "$API_PATH" all-dev` |
| Both prod | API + frontend | `make -C "$API_PATH" all-prod` |

All Makefile targets use `AWS_PROFILE=boopixel` by default.

---

## Workflow

1. **Resolve paths.** Run the discovery block above. Abort and ask if either is empty.
2. **Identify target.** Ask if ambiguous — never guess between dev/prod.
3. **Check git state** before prod deploys:
   - API: `git -C "$API_PATH" status && git -C "$API_PATH" log -1 --oneline`
   - Frontend: `git -C "$FRONTEND_PATH" status && git -C "$FRONTEND_PATH" log -1 --oneline`
   - If there are uncommitted changes the user expects to deploy, warn before proceeding.
4. **Frontend via git push (alternative path).** Pushing to `master` on business-frontend triggers Amplify automatically (webhook). Only use `frontend-prod` target when the user wants a manual rebuild without a new commit.
5. **API deploy always runs through SAM** — there is no git-triggered deploy for the API. A commit on master does NOT deploy the API.
6. **Run the Make target.** Show command before running. For prod, confirm with the user unless they explicitly said "deploy prod".
7. **Report the outcome.** On success:
   - API: grab `ApiUrl` via `aws cloudformation describe-stacks --stack-name business-api-prod --query 'Stacks[0].Outputs' --profile boopixel --region us-east-1`
   - Frontend: report the Amplify `jobId` and `status` printed by the Makefile.

---

## Prod deploy checklist

Before running `deploy-prod` or `all-prod`:

- [ ] Current branch is `master` on the repo being deployed
- [ ] Working tree is clean (or user explicitly wants a dirty deploy)
- [ ] `$API_PATH/samconfig.toml` exists (not just the `.example`) — required for API
- [ ] For API: `samconfig.toml` has a `[prod]` section with real `DatabaseUrl`, `SecretKey`, `CorsOrigins`

If any check fails, stop and tell the user — do not try to "fix" secrets or configs without explicit instruction.

---

## Common requests → command

| User says | Run |
|---|---|
| "deploy api" / "deploy a api em prod" | `make -C "$API_PATH" deploy-prod` |
| "deploy api dev" | `make -C "$API_PATH" deploy-dev` |
| "deploy frontend" / "deploy front em prod" | push to master (if commits pending) OR `make -C "$API_PATH" frontend-prod` |
| "deploy tudo" / "deploy everything" | `make -C "$API_PATH" all-prod` |
| "rebuild frontend sem commit" | `make -C "$API_PATH" frontend-prod` |

---

## Rollback

- **API prod:** redeploy the previous commit (`git -C "$API_PATH" checkout <sha> && make -C "$API_PATH" deploy-prod`) or `sam delete --config-env prod --profile boopixel` to tear the stack down (destructive — always confirm).
- **Frontend:** redeploy previous commit via Amplify console, or revert the commit and push.

Never run `sam delete` without explicit user confirmation.

---

## Troubleshooting

- **Discovery returns empty** — ask the user where the repo lives; offer to save the path in `~/.claude/boopixel-deploy.env` for next time.
- **`sam build` fails with "Python 3.13 not found"** — user must `pyenv install 3.13` locally.
- **CORS errors post-deploy** — `CorsOrigins` in `samconfig.toml` must be valid JSON array, e.g. `["https://app.boopixel.com"]`.
- **Amplify `start-job` returns `ResourceNotFoundException`** — check `AMPLIFY_APP_ID_*` vars in the Makefile still match the live app.
- **401 on every request after API deploy** — `SECRET_KEY` changed; existing tokens are invalid. Expected if the user rotated it.

Authoritative deploy docs: `$API_PATH/DEPLOY.md`.

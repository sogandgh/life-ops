# LaTeX setup

`build_pdf.sh` needs a LaTeX engine, and prefers to compile inside the
**`texlive/texlive:latest` Docker image** — the full TeX Live distribution, so no package or
font is ever missing and nothing LaTeX-related has to be installed on the machine.

Nothing here is needed unless the master resume is a `.tex` file. A Markdown or plain-text
resume works fine for assessment and edit proposals without any of this.

## Option 1 — Docker (recommended)

1. Install Docker Desktop (or any Docker daemon).
2. Make sure the daemon is running. If a build fails with "daemon isn't running", start
   Docker, give it ~20 seconds, and re-run.
3. `build_pdf.sh` pulls the image automatically the first time (several GB, one time only).
   To do it by hand:

   ```bash
   docker pull texlive/texlive:latest
   ```

## Option 2 — Local pdflatex

The script falls back to a local `pdflatex` if one exists and Docker is unavailable. It
searches `PATH`, `/Library/TeX/texbin`, and `/usr/local/texlive/*/bin/*`.

Be aware of what minimal distributions cost you. BasicTeX (~400 MB) typically needs a round
of `sudo tlmgr install` for common resume-template packages (`preprint`, `titlesec`,
`marvosym`, `enumitem`), and can then still fail on a missing Type 1 font outline — minimal
distributions ship font *metrics* without the *outlines*, so this class of failure keeps
recurring. If a build fails on a missing font, install the full scheme
(`sudo tlmgr install scheme-full`) or switch to Docker.

On macOS: `brew install --cask mactex` for the full distribution, or
`brew install --cask basictex` for the minimal one plus the caveats above.

## Verify

```bash
./build_pdf.sh /path/to/resume.tex --out-dir /tmp/resume-test --base Test_Resume
```

Expect `BUILT: /tmp/resume-test/Test_Resume-1.pdf`, an `ENGINE:` line, and `PAGES: 1`.

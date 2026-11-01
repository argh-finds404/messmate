# Learning Log

## Entry: Mutation Testing with mutmut

- **Date:** 2026-11-01
- **What I tried:** 
  I tried running mutation testing using `mutmut` to see if our unit test suite actually catches bugs rather than just giving high code coverage. I configured it to mutate `app/services/`, `app/adapters/`, and `app/validation.py`.
- **What broke:** 
  First, `mutmut` does not run on native Windows because it relies on Linux process forking. When I switched to WSL Ubuntu, `python3-venv` and `pip` were missing, so I had to install them via `apt`. Then, during the initial run, `mutmut` threw an import error because test files inside the isolated `mutants/` directory couldn't find the `app` module.
- **Resource used:** 
  `mutmut` official documentation and Pytest configuration guides.
- **Verdict on the resource:** 
  Very useful once configured properly. Adding `also_copy = app/` in `setup.cfg` fixed the module import issue in the mutant copies. The tool took around 20 minutes to learn and run, but it quickly pointed out 9 real assertion gaps in our validation messages and payment calculations that standard 100% statement coverage had completely missed.
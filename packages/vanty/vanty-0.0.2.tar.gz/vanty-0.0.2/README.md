# <img style="margin-right: 2px; margin-top: 10px" alt="logo" height="12" width="12" src="https://cdn.advantch.com/static/images/logo.png"> Vanty CLI

CLI for managing projects from advantch.com including:

- Vanty Starter Kit

   This  Vanty Starter Kit is the fastest way to launch new SaaS & AI products.

   Visit https://www.advantch.com/ for documentation and more information

## Installation

We recommend using pipx to install vanty:

```bash
pipx install vanty
```

## Usage

1. Verify your license:

   ```bash
   vanty verify --license <your-license-id>
   ```

2. Download the project to the current directory:

   ```bash
   vanty project download
   ```

3. Get started:

   ```bash
   cd <project-name>
   vanty dev init
   ```

4. Run the project:

   ```bash
    vanty dev run
    ```

## Issues & Support:

Advantch users can report issues on the slack issue channel.

- https://www.advantch.com/issues/

## PRs and Contributions:

Please note that whilst this is open source, it is not intended to be a community project.

Advantch users can submit PRs for extensions etc that maybe helpful to the core project or other users.

Otherwise, please fork and use this as a base for your own projects.
 
2023 &centerdot; Advantch.

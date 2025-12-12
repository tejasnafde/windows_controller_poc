# GitHub Actions CI/CD Pipeline

This directory contains the GitHub Actions workflow for automatically building and releasing the MyOptum Installer executable.

## Workflow: `build-release.yml`

### Trigger
- **Automatic**: Runs on every push to `main` or `master` branch
- **Manual**: Can be triggered manually from the Actions tab

### What it does

1. **Checkout Code**: Pulls the latest code from the repository
2. **Setup Python**: Installs Python 3.11 on the Windows runner
3. **Install Dependencies**: Runs `pip install -r requirements.txt`
4. **Auto-increment Version**: 
   - Reads the current version from `build_executable.py`
   - Increments the patch version (e.g., 0.0.4 → 0.0.5)
   - Updates the version in the file
5. **Commit Version Bump**: Commits the version change back to the repository
6. **Build Executable**: Runs `python build_executable.py`
7. **Rename with Version**: Renames the output to include version (e.g., `MyOptum_Installer_v0.0.5.exe`)
8. **Create Release**: Creates a new GitHub release with the version tag
9. **Upload Asset**: Uploads the executable to the release

### Requirements

#### Repository Settings
You need to configure your repository to allow GitHub Actions to create releases:

1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
3. Click **Save**

### Downloading the Executable

After each successful build:

1. Go to the **Releases** section of your repository
2. Find the latest release (e.g., `v0.0.5`)
3. Download the executable file (e.g., `MyOptum_Installer_v0.0.5.exe`)
4. Run it on your Windows machine

### Runner Information

- **OS**: `windows-latest` (currently Windows Server 2022, which is compatible with Windows 11)
- **Python**: 3.11
- **Build Time**: Typically 5-10 minutes per build

### Skipping CI

If you want to push changes without triggering a build, include `[skip ci]` in your commit message:

```bash
git commit -m "docs: update README [skip ci]"
```

### Manual Trigger

You can manually trigger a build:

1. Go to **Actions** tab
2. Select **Build and Release Windows Executable**
3. Click **Run workflow**
4. Select the branch and click **Run workflow**

### Troubleshooting

#### Build Fails
- Check the Actions tab for detailed logs
- Ensure all dependencies are in `requirements.txt`
- Verify that `build_executable.py` runs successfully locally

#### Version Not Incrementing
- The workflow reads the `VERSION` variable from `build_executable.py`
- Ensure the format is exactly: `VERSION = "X.Y.Z"`

#### Release Not Created
- Verify repository permissions (see Requirements above)
- Check that `GITHUB_TOKEN` has sufficient permissions
- Ensure the tag doesn't already exist

#### Executable Not Uploaded
- Check that `build_executable.py` creates the file in `dist/MyOptum_Installer.exe`
- Verify the rename step completes successfully

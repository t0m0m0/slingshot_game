# Setting Up GitHub Repository

Follow these steps to push your local repository to GitHub:

## 1. Create a new repository on GitHub

1. Go to [GitHub](https://github.com/) and sign in to your account
2. Click the "+" icon in the top right corner and select "New repository"
3. Enter "slingshot-game" as the repository name
4. Add a description (optional)
5. Choose whether to make the repository public or private
6. Do NOT initialize the repository with a README, .gitignore, or license (we've already created these locally)
7. Click "Create repository"

## 2. Connect your local repository to GitHub

After creating the repository, GitHub will show you commands to push an existing repository. Run the following commands in your local repository:

```bash
cd /home/yuaioiaiu/q/slingshot_game
git remote add origin https://github.com/YOUR_USERNAME/slingshot-game.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## 3. Verify the repository

1. Go to `https://github.com/YOUR_USERNAME/slingshot-game`
2. Ensure all your files are visible in the repository

## 4. Set up GitHub Pages (optional)

If you want to create a project website:

1. Go to your repository settings
2. Scroll down to the "GitHub Pages" section
3. Select the "main" branch and "/docs" folder as the source
4. Click "Save"

Your project site will be available at `https://YOUR_USERNAME.github.io/slingshot-game/`

## 5. Collaborating with others

To allow others to contribute to your project:

1. Go to your repository settings
2. Click on "Manage access"
3. Click "Invite a collaborator"
4. Enter the GitHub username or email address of the person you want to invite
5. Click "Add [username] to this repository"

## 6. Regular workflow

For ongoing development:

```bash
# Pull latest changes
git pull origin main

# Make changes to files

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push changes
git push origin main
```

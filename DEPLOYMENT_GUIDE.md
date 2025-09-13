# Deployment Guide - Streamlit Cloud

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and log in
2. Click "New repository" (green button)
3. Repository name: `retirement-income-dashboard`
4. Description: `Retirement Income Calculator Dashboard for Asset Guidance Group`
5. Set to **Public** (required for free Streamlit Cloud)
6. Click "Create repository"

## Step 2: Push Code to GitHub

Run these commands in your terminal:

```bash
cd "C:\Users\wrnag\RIdashboard"
git remote add origin https://github.com/YOUR_USERNAME/retirement-income-dashboard.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your repositories
4. Click "New app"
5. Select:
   - Repository: `retirement-income-dashboard`
   - Branch: `main`
   - Main file path: `retirement_dashboard.py`
6. Click "Deploy!"

## Step 4: Get Your App URL

After deployment (2-3 minutes), you'll get a URL like:
`https://retirement-income-dashboard-YOUR_USERNAME.streamlit.app`

## Step 5: Embed on Your Website

Add this HTML to your website page at `assetguidancegroup.com/retirement-income-dashboard`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Retirement Income Dashboard - Asset Guidance Group</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { margin: 0; font-family: Arial, sans-serif; }
        .header { 
            background: #1E3A8A; 
            color: white; 
            padding: 20px; 
            text-align: center; 
        }
        iframe { border: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Retirement Income Calculator</h1>
        <p>Professional retirement planning analysis by Asset Guidance Group</p>
    </div>
    
    <iframe src="YOUR_STREAMLIT_URL_HERE" 
            width="100%" 
            height="900px"
            title="Retirement Income Calculator">
    </iframe>
</body>
</html>
```

## Troubleshooting

- **App won't load**: Check requirements.txt includes all dependencies
- **Errors in logs**: View logs in Streamlit Cloud dashboard
- **Updates not showing**: GitHub pushes auto-deploy to Streamlit Cloud

## Custom Domain (Optional)

For a professional URL like `dashboard.assetguidancegroup.com`:
1. Upgrade to Streamlit Cloud Pro ($20/month)
2. Add custom domain in app settings
3. Update DNS CNAME record

Your dashboard is now ready for client use!
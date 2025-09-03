# My Awesome Blog

A personal blog built with [Hugo](https://gohugo.io/) and the [Hugo Blog Awesome](https://github.com/hugo-sid/hugo-blog-awesome) theme.

## Features

- 🚀 Fast static site generation with Hugo
- 📱 Responsive design with the Blog Awesome theme
- 🔍 Built-in search functionality
- 📝 Markdown-based content management
- 🎨 Customizable appearance and features
- 📊 Reading time and word count
- 🔗 Social media integration

## Getting Started

### Prerequisites

- [Hugo](https://gohugo.io/installation/) (Extended version recommended)
- Git

### Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd blog
   ```

2. Install the theme (if not already done):
   ```bash
   git submodule update --init --recursive
   ```

3. Start the development server:
   ```bash
   hugo server -D
   ```

4. Open your browser and visit `https://sebkrantz.github.io`

### Creating Content

- **New blog post:**
  ```bash
  hugo new content posts/my-new-post.md
  ```

- **New page:**
  ```bash
  hugo new content my-new-page.md
  ```

### Building for Production

```bash
hugo
```

The generated site will be in the `public/` directory.

## Configuration

Edit `hugo.toml` to customize:

- Site title and description
- Author information
- Social media links
- Theme features and appearance
- Navigation settings

## Theme Features

The Hugo Blog Awesome theme includes:

- Dark/light mode toggle
- Code syntax highlighting
- Math equation support (KaTeX)
- Mermaid diagram support
- Table of contents
- Related posts
- Social sharing buttons
- Search functionality
- Reading progress indicator

## Deployment

This site can be deployed to various platforms:

- **Netlify**: Connect your Git repository for automatic deployments
- **Vercel**: Deploy with zero configuration
- **GitHub Pages**: Use GitHub Actions for automated builds
- **Any static hosting**: Upload the `public/` folder contents

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Feel free to submit issues and enhancement requests!

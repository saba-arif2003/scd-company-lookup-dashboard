# Company Lookup Dashboard - Frontend

A modern, responsive React application for searching company information, stock prices, and SEC filings.

## 🚀 Features

- **Company Search**: Search by company name or ticker symbol
- **Real-time Stock Data**: Current prices, market cap, and trading volume
- **SEC Filings**: Access to recent 10-K, 10-Q, and 8-K reports
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Professional UI**: Clean, modern interface with smooth animations
- **Fast Performance**: Optimized loading and caching strategies

## 🛠 Technology Stack

- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Hot Toast** - Toast notifications
- **Heroicons** - Beautiful SVG icons
- **Date-fns** - Date formatting utilities

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development server**
   ```bash
   npm start
   ```

The application will be available at `http://localhost:3000`

## 🏗 Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## 🐳 Docker Deployment

Build and run with Docker:

```bash
docker build -t company-lookup-frontend .
docker run -p 3000:3000 company-lookup-frontend
```

Or use Docker Compose:

```bash
docker-compose up --build
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static files
├── src/
│   ├── components/         # React components
│   │   ├── common/        # Reusable components
│   │   ├── search/        # Search components
│   │   └── dashboard/     # Dashboard components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API services
│   ├── styles/            # CSS and styling
│   ├── utils/             # Utility functions
│   ├── App.jsx            # Main app component
│   └── index.js           # Entry point
├── package.json           # Dependencies
├── tailwind.config.js     # Tailwind configuration
└── README.md             # This file
```

## 🎨 Styling

The application uses Tailwind CSS for styling with a custom design system:

- **Colors**: Professional blue/gray palette
- **Typography**: Inter font family for readability
- **Components**: Reusable UI components with consistent styling
- **Responsive**: Mobile-first design approach

## 🔧 Configuration

### Environment Variables

- `REACT_APP_API_BASE_URL` - Backend API URL (required)
- `REACT_APP_ENV` - Environment name
- `REACT_APP_VERSION` - Application version
- `REACT_APP_DEBUG_MODE` - Enable debug features

### API Integration

The frontend communicates with the backend API through:

- **Search Endpoint**: `/api/v1/search`
- **Company Lookup**: `/api/v1/company/lookup`
- **Stock Data**: `/api/v1/stock/{ticker}`
- **SEC Filings**: `/api/v1/filings/{cik}`

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## ♿ Accessibility

- WCAG 2.1 AA compliance
- Semantic HTML structure
- Keyboard navigation support
- Screen reader friendly
- High contrast colors

## 🔍 Search Features

- **Auto-suggestions**: Real-time search suggestions
- **Recent searches**: Previously searched companies
- **Fuzzy matching**: Smart search algorithm
- **Error handling**: Graceful error states
- **Loading states**: Smooth loading experiences

## 📊 Data Display

- **Company Cards**: Comprehensive company information
- **Stock Cards**: Real-time price data with change indicators
- **Filing Tables**: Sortable and filterable SEC filings
- **Error States**: User-friendly error messages
- **Empty States**: Helpful guidance when no data

## 🚀 Performance

- **Code splitting**: Lazy loading of components
- **Caching**: Intelligent API response caching
- **Optimized images**: Responsive image loading
- **Bundle optimization**: Minimized JavaScript bundles
- **Service worker**: Offline capabilities (coming soon)

## 🧪 Testing

Run tests with:

```bash
npm test
```

## 🔧 Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Code Standards

- **ESLint**: Code linting and error checking
- **Prettier**: Code formatting
- **Conventional Commits**: Commit message standards

## 🚢 Deployment

### Vercel (Recommended)

1. Connect your repository to Vercel
2. Set environment variables
3. Deploy automatically on push

### Netlify

1. Connect repository
2. Set build command: `npm run build`
3. Set publish directory: `build`

### Traditional Hosting

1. Run `npm run build`
2. Upload `build` folder to your web server
3. Configure server to serve `index.html` for all routes

## 🐛 Troubleshooting

### Common Issues

**API Connection Issues**
- Check `REACT_APP_API_BASE_URL` environment variable
- Ensure backend is running and accessible
- Check CORS configuration

**Build Failures**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (requires 16+)
- Verify all environment variables are set

**Styling Issues**
- Rebuild Tailwind CSS: `npm run build:css`
- Check for conflicting CSS rules
- Verify Tailwind configuration

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Contact the development team
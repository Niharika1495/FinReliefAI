# FinRelief AI - Frontend Architecture

The frontend of FinRelief AI is a single page application built on **React.js** powered by the **Vite** bundler and styled using **Tailwind CSS**. It communicates with the FastAPI backend over HTTP using **Axios**.

---

## Folder Architecture

The source code resides under `src/`, structured as follows:

```
src/
├── assets/       # Static assets (images, logos, SVG files)
├── components/   # Modular, reusable UI components (common buttons, inputs, widgets)
├── layouts/      # Visual structure shells (Dashboard layout, Auth view shell)
├── pages/        # Router view targets (Dashboard, Analysis, History, Login)
├── hooks/        # Shared custom React hooks (useAuth, useLocalStorage)
├── context/      # Context providers (Session context, Calculation states)
├── services/     # API integration logic using Axios client singletons
├── utils/        # Generic frontend utility helper functions
├── routes/       # Centralized route definitions and navigation guards
└── styles/       # Tailwind directive setups and custom CSS themes
```

---

## Design System & Styling

To maintain a premium, state-of-the-art visual standard:
1. **Typography**: The primary typeface is **Outfit** (loaded via Google Fonts), providing a sleek, modern appearance.
2. **Color Palette**: Tailored Tailwind configuration includes a base dark slate interface (`bg-slate-950`), custom green emerald accents, and teal gradients.
3. **Glassmorphism**: Defined inside `src/styles/index.css` via utility classes to achieve backdrop-blur cards and modules:
   ```html
   <div class="glassmorphism glow-green p-6 rounded-xl">...</div>
   ```

---

## Development Setup

### 1. Install Dependencies
Run the installation command inside the `frontend` folder:
```bash
npm install
```

### 2. Start Development Server
Boot Vite's build server:
```bash
npm run dev
```
The application will launch locally at: [http://localhost:3000](http://localhost:3000)

### 3. Build & Preview
To run production compilations:
```bash
npm run build
npm run preview
```

---

## Conventions
1. **API Requests**: All interactions with the API must go through the functions defined in `src/services/`. Never place inline Axios fetch commands inside page components.
2. **Context vs Hooks**: Use Context Providers for long-lived global state (like user authorization status). For data-fetching and temporary states, use custom hooks.
3. **Responsive Design**: Ensure pages are designed mobile-first using responsive prefix variants (`sm:`, `md:`, `lg:`).

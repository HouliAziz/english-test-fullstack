/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: [
    '@radix-ui/react-progress',
    '@radix-ui/react-avatar',
    '@radix-ui/react-dropdown-menu',
    '@radix-ui/react-tooltip',
    '@radix-ui/react-dialog',
    '@radix-ui/react-alert-dialog',
    '@radix-ui/react-tabs',
    '@radix-ui/react-switch',
    '@radix-ui/react-popover',
    '@radix-ui/react-radio-group',
    '@radix-ui/react-checkbox',
    '@radix-ui/react-select',
    '@radix-ui/react-toast',
    '@radix-ui/react-accordion',
    '@radix-ui/react-collapsible',
    '@radix-ui/react-context-menu',
    '@radix-ui/react-label',
    '@radix-ui/react-separator',
    '@radix-ui/react-slider',
    '@radix-ui/react-toggle',
    '@radix-ui/react-toggle-group',
    '@radix-ui/react-navigation-menu',
    '@radix-ui/react-menubar',
    '@radix-ui/react-aspect-ratio',
    '@radix-ui/react-hover-card',
    '@radix-ui/react-scroll-area',
    '@radix-ui/react-resizable',
    '@radix-ui/react-sheet',
    '@radix-ui/react-sonner',
    // ...any other @radix-ui/react-* you use
  ],
  output: 'export',
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },
};

module.exports = nextConfig;

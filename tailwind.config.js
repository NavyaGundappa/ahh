module.exports = {
    content: [
        './templates/**/*.html',
        './static/js/**/*.js',
    ],
    theme: {
        extend: {
            colors: {
                // A more professional and cohesive color palette
                'brand': {
                    'dark': '#0D2C54',    // Deep navy for primary headings
                    'primary': '#2A9D8F', // Teal for buttons, links, and accents
                    'light': '#E9C46A',   // A secondary accent color (optional)
                },
                'neutral': {
                    '900': '#111827', // For body text
                    '50': '#F9FAFB',  // For light backgrounds
                }
            },
            fontFamily: {
                sans: ['Poppins', 'sans-serif'],
            },
            // Adding custom typography styles for a better reading experience
            typography: ({ theme }) => ({
                DEFAULT: {
                    css: {
                        '--tw-prose-body': theme('colors.neutral[900]'),
                        '--tw-prose-headings': theme('colors.brand.dark'),
                        '--tw-prose-links': theme('colors.brand.primary'),
                        '--tw-prose-bold': theme('colors.brand.dark'),
                        '--tw-prose-bullets': theme('colors.brand.primary'),
                        '--tw-prose-quotes': theme('colors.brand.dark'),
                        '--tw-prose-quote-borders': theme('colors.brand.primary'),
                    },
                },
            }),
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
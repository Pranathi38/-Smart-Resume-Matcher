import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Smart Resume Matcher',
  description: 'Neural Resume Matching with Semantic Search',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-dark-900 text-dark-50">
        {children}
      </body>
    </html>
  )
}

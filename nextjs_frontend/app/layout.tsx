import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ApprovedDocumentsProvider } from '../contexts/ApprovedDocumentsContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Documentation Maintainer',
  description: 'Review and manage documentation updates',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ApprovedDocumentsProvider>
          <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="container mx-auto px-4">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center space-x-8">
                  <a href="/" className="text-xl font-bold text-gray-900">
                    📚 Documentation Maintainer
                  </a>
                  <div className="flex space-x-4">
                    <a
                      href="/"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Search & Review
                    </a>
                    <a
                      href="/chat"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      💬 Chat
                    </a>
                    <a
                      href="/final-review"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Final Review
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </nav>
          <div className="pt-0">
            {children}
          </div>
        </ApprovedDocumentsProvider>
      </body>
    </html>
  )
} 
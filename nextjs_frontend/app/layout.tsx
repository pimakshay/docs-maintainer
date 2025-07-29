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
          {children}
        </ApprovedDocumentsProvider>
      </body>
    </html>
  )
} 
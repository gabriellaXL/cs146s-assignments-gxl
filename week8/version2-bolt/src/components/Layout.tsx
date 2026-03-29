import { ReactNode } from 'react';
import { FileText, Plus } from 'lucide-react';
import { useRouter } from '../lib/router';
import { Button } from './ui/Button';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { navigate } = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-gray-900 hover:text-gray-600 transition-colors"
            >
              <FileText className="w-6 h-6" />
              <h1 className="text-xl font-semibold">Developer Control Center</h1>
            </button>
            <Button
              onClick={() => navigate('/notes/new')}
              className="flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Note
            </Button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}

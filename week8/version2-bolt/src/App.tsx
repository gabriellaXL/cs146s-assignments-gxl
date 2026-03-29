import { RouterProvider } from './lib/router';
import { parseRoute } from './lib/route-utils';
import { useRouter } from './lib/router-context';
import { Layout } from './components/Layout';
import { NotesList } from './pages/NotesList';
import { NoteDetail } from './pages/NoteDetail';
import { NoteForm } from './pages/NoteForm';

function AppContent() {
  const { currentPath } = useRouter();

  let content;

  if (currentPath === '/' || currentPath === '') {
    content = <NotesList />;
  } else if (currentPath === '/notes/new') {
    content = <NoteForm />;
  } else if (parseRoute('/notes/:id/edit', currentPath)) {
    content = <NoteForm />;
  } else if (parseRoute('/notes/:id', currentPath)) {
    content = <NoteDetail />;
  } else {
    content = (
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">404 - Page Not Found</h1>
        <p className="text-gray-600">The page you're looking for doesn't exist.</p>
      </div>
    );
  }

  return <Layout>{content}</Layout>;
}

function App() {
  return (
    <RouterProvider>
      <AppContent />
    </RouterProvider>
  );
}

export default App;

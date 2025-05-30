import { BrowserRouter as Router, Routes, Route, Link, Navigate, useNavigate, useLocation } from 'react-router-dom'
import Training from './Training'
import Profile from './Profile'
import Reference from './Reference'
import Auth from './Auth'
import { ProtectedRoute } from './ProtectedRoute';
import PhraseBuilder from './PhraseBuilder';
import WordForm from './WordForm';
import { useAuth } from './api/ApiConfigContext';
import WordView from './WordView';
import { useReadWordApiWordsWordIdGet } from './api/words/words';
import styles from './App.module.css';
import MistakeStats from './MistakeStats';
import Search from './Search';
import PhraseView from './PhraseView';
import SemanticGroupView from './SemanticGroupView';
import ComponentView from './ComponentView';
import SemanticGroupForm from './SemanticGroupForm';
import WordComponentForm from './WordComponentForm';
import { Container, Navbar, Nav, Button } from 'react-bootstrap';
import { useCreateSemanticGroupApiSemanticGroupsPost } from './api/semantic-groups/semantic-groups';
import { useState } from 'react';

function NavBar() {
  const { token, setToken } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    setToken(null);
    navigate('/auth');
  };

  return (
    <Navbar bg="light" expand="lg" className="mb-4" style={{ width: '100%' }}>
      <Container fluid>
        <Navbar.Brand as={Link} to="/">Language App</Navbar.Brand>
        <Nav className="me-auto">
          <Nav.Link as={Link} to="/training">Training</Nav.Link>
          <Nav.Link as={Link} to="/profile">Profile</Nav.Link>
          <Nav.Link as={Link} to="/reference">Reference</Nav.Link>
          <Nav.Link as={Link} to="/mistake-stats">Mistake Stats</Nav.Link>
          <Nav.Link as={Link} to="/search">Search</Nav.Link>
        </Nav>
      {token && (
          <Button variant="outline-danger" onClick={handleLogout} className="ms-auto">Logout</Button>
      )}
      </Container>
    </Navbar>
  );
}

function WordFormWrapper() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const id = params.get('id');
  const wordId = id ? Number(id) : undefined;
  const { data, isLoading, error } = useReadWordApiWordsWordIdGet(wordId || 0);

  if (wordId && isLoading) return <div>Loading word...</div>;
  if (wordId && error) return <div>Error loading word.</div>;

  return <WordForm word={wordId && data?.data ? data.data : undefined} />;
}

function SemanticGroupFormWrapper() {
  const navigate = useNavigate();
  const createGroup = useCreateSemanticGroupApiSemanticGroupsPost();
  const [status, setStatus] = useState<string | null>(null);

  return (
    <div>
      <SemanticGroupForm
        submitLabel="Create Semantic Group"
        onSubmit={data => {
          setStatus(null);
          createGroup.mutate(
            { data },
            {
              onSuccess: (resp: any) => {
                setStatus('Semantic group created!');
                if (resp?.data?.id) {
                  navigate(`/semantic-group?id=${resp.data.id}`);
                }
              },
              onError: (err: any) => {
                setStatus('Error: ' + (err?.message || 'Unknown error'));
              },
            }
          );
        }}
      />
      {status && <div style={{ marginTop: 12 }}>{status}</div>}
    </div>
  );
}

function App() {
  return (
    <div style={{ minHeight: '100vh', background: '#f8f9fa' }}>
    <Router>
      <NavBar />
        <Container fluid style={{ minHeight: '90vh' }}>
      <Routes>
        <Route path="/auth" element={<Auth />} />
        <Route path="/training" element={<ProtectedRoute><Training /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/reference" element={<ProtectedRoute><Reference /></ProtectedRoute>} />
        <Route path="/mistake-stats" element={<ProtectedRoute><MistakeStats /></ProtectedRoute>} />
        <Route path="/phrase-builder" element={<ProtectedRoute><PhraseBuilder /></ProtectedRoute>} />
        <Route path="/word-form" element={<ProtectedRoute><WordFormWrapper /></ProtectedRoute>} />
        <Route path="/word" element={<ProtectedRoute><WordView /></ProtectedRoute>} />
        <Route path="/search" element={<ProtectedRoute><Search /></ProtectedRoute>} />
        <Route path="/phrase" element={<ProtectedRoute><PhraseView /></ProtectedRoute>} />
        <Route path="/semantic-group" element={<ProtectedRoute><SemanticGroupView /></ProtectedRoute>} />
        <Route path="/component" element={<ProtectedRoute><ComponentView /></ProtectedRoute>} />
            <Route path="/semantic-group-form" element={<ProtectedRoute><SemanticGroupFormWrapper /></ProtectedRoute>} />
            <Route path="/component-form" element={<ProtectedRoute><WordComponentForm /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/reference" replace />} />
      </Routes>
        </Container>
    </Router>
    </div>
  )
}

export default App

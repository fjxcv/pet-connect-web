import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import Footer from './components/Footer';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import AddPet from './pages/AddPet';
import AdminDashboard from './pages/AdminDashboard';
import CmsDetail from './pages/CmsDetail';
import CmsList from './pages/CmsList';
import CommunityList from './pages/CommunityList';
import CommunityPostDetail from './pages/CommunityPostDetail';
import CommunityPublish from './pages/CommunityPublish';
import CommunityPostEdit from './pages/CommunityPostEdit';
import Dashboard from './pages/Dashboard';
import ForgotPassword from './pages/ForgotPassword';
import Home from './pages/Home';
import Login from './pages/Login';
import LostFoundDetail from './pages/LostFoundDetail';
import LostFoundList from './pages/LostFoundList';
import LostFoundPublish from './pages/LostFoundPublish';
import MyPets from './pages/MyPets';
import PetDetail from './pages/PetDetail';
import PetList from './pages/PetList';
import Register from './pages/Register';
import RescueList from './pages/RescueList';
import RescueReport from './pages/RescueReport';
import AccountCenter from './pages/AccountCenter';
import UserProfile from './pages/UserProfile';
import UserPublicProfile from './pages/UserPublicProfile';
import AdminRoute from './components/AdminRoute';
import { ManageModeProvider } from './context/ManageModeContext';
import { AuthPromptProvider } from './context/AuthPromptContext';
import AiAssistantWidget from './components/AiAssistantWidget';

function App() {
  return (
    <Router>
      <ManageModeProvider>
      <AuthPromptProvider>
      <div className="App d-flex flex-column min-vh-100">
        <Navbar />
        <AiAssistantWidget />
        <main className="flex-grow-1">
          <div className="container mt-4">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/pets" element={<PetList />} />
              <Route path="/pets/:id" element={<PetDetail />} />
              <Route path="/cms" element={<CmsList />} />
              <Route path="/cms/:id" element={<CmsDetail />} />
              <Route path="/lost-found" element={<LostFoundList />} />
              <Route path="/lost-found/publish" element={<ProtectedRoute><LostFoundPublish /></ProtectedRoute>} />
              <Route path="/lost-found/:id" element={<LostFoundDetail />} />
              <Route path="/community" element={<CommunityList />} />
              <Route path="/community/publish" element={<ProtectedRoute><CommunityPublish /></ProtectedRoute>} />
              <Route path="/community/:id/edit" element={<ProtectedRoute><CommunityPostEdit /></ProtectedRoute>} />
              <Route path="/community/:id" element={<CommunityPostDetail />} />
              <Route path="/rescue" element={<RescueList />} />
              <Route path="/rescue/report" element={<ProtectedRoute><RescueReport /></ProtectedRoute>} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/admin" element={<ProtectedRoute><AdminRoute><AdminDashboard /></AdminRoute></ProtectedRoute>} />
              <Route path="/users/:id" element={<UserPublicProfile />} />
              <Route path="/account" element={<ProtectedRoute><AccountCenter /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
              <Route path="/my-pets" element={<ProtectedRoute><MyPets /></ProtectedRoute>} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/add-pet" element={<ProtectedRoute><AddPet /></ProtectedRoute>} />
            </Routes>
          </div>
        </main>
        <Footer />
      </div>
      </AuthPromptProvider>
      </ManageModeProvider>
    </Router>
  );
}

export default App;

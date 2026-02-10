import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  Store,
  Users,
  MessageSquare,
  Megaphone,
  ShoppingCart,
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import api from '../services/api';

// Placeholder components - você implementará depois
const DashboardHome = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {[
        { title: 'Total de Restaurantes', value: '0', color: 'bg-blue-500' },
        { title: 'Leads Ativos', value: '0', color: 'bg-green-500' },
        { title: 'Mensagens Hoje', value: '0', color: 'bg-yellow-500' },
        { title: 'Campanhas Ativas', value: '0', color: 'bg-purple-500' }
      ].map((stat, index) => (
        <div key={index} className="bg-white p-6 rounded-lg shadow">
          <div className={`${stat.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
            <LayoutDashboard className="text-white" />
          </div>
          <h3 className="text-gray-600 text-sm">{stat.title}</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
        </div>
      ))}
    </div>
  </div>
);

const Restaurants = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">Restaurantes</h1>
    <p className="text-gray-600">Gerencie seus restaurantes aqui.</p>
  </div>
);

const Leads = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">CRM - Leads</h1>
    <p className="text-gray-600">Kanban de leads em desenvolvimento.</p>
  </div>
);

const Messages = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">Central de Atendimento</h1>
    <p className="text-gray-600">Chat WhatsApp em desenvolvimento.</p>
  </div>
);

const Campaigns = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">Disparador de Marketing</h1>
    <p className="text-gray-600">Campanhas de marketing em desenvolvimento.</p>
  </div>
);

const Products = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-6">Catálogo de Produtos</h1>
    <p className="text-gray-600">Gerencie seu catálogo aqui.</p>
  </div>
);

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/dashboard/restaurants', icon: Store, label: 'Restaurantes' },
    { path: '/dashboard/leads', icon: Users, label: 'CRM - Leads' },
    { path: '/dashboard/messages', icon: MessageSquare, label: 'Atendimento' },
    { path: '/dashboard/campaigns', icon: Megaphone, label: 'Marketing' },
    { path: '/dashboard/products', icon: ShoppingCart, label: 'Catálogo' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transition-transform duration-300 ease-in-out`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-6 py-6 border-b">
            <div>
              <h1 className="text-xl font-bold text-gray-900">SaaS CRM</h1>
              <p className="text-sm text-gray-600">Multi-Restaurante</p>
            </div>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="lg:hidden text-gray-600 hover:text-gray-900"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Menu */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Info & Logout */}
          <div className="border-t px-4 py-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">
                  {user?.full_name?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.full_name}
                </p>
                <p className="text-xs text-gray-600 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 w-full px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Sair</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Overlay para mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm px-6 py-4 lg:hidden">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="text-gray-600 hover:text-gray-900"
          >
            <Menu className="w-6 h-6" />
          </button>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            <Route path="/restaurants" element={<Restaurants />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/products" element={<Products />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;

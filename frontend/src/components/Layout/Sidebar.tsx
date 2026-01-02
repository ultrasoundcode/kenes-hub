'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Home,
  FileText,
  MessageSquare,
  Users,
  Settings,
  BarChart,
  Bell,
  Bot,
  DocumentText,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

interface SidebarProps {
  isOpen: boolean;
}

const menuItems = [
  { name: 'Главная', href: '/dashboard', icon: Home },
  { name: 'Заявки', href: '/applications', icon: FileText },
  { name: 'Документы', href: '/documents', icon: DocumentText },
  { name: 'Чат', href: '/chat', icon: MessageSquare },
  { name: 'AI Помощник', href: '/ai-assistant', icon: Bot },
  { name: 'Уведомления', href: '/notifications', icon: Bell },
  { name: 'Аналитика', href: '/analytics', icon: BarChart },
  { name: 'Пользователи', href: '/users', icon: Users },
  { name: 'Настройки', href: '/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  const pathname = usePathname();
  const { user } = useAuth();

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  const filteredMenuItems = menuItems.filter((item) => {
    // Фильтруем пункты меню в зависимости от роли пользователя
    if (user?.role === 'borrower') {
      return ['Главная', 'Заявки', 'Документы', 'Чат', 'AI Помощник', 'Уведомления'].includes(
        item.name
      );
    }
    return true;
  });

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 lg:shadow-none ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-center h-16 px-4 bg-primary-600">
          <h1 className="text-xl font-bold text-white">Kenes Hub</h1>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                  active
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user?.first_name?.[0] || 'U'}
                </span>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-gray-500">{user?.role}</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
import React from 'react';
import { LineChart, BarChart3, Bot } from 'lucide-react';

interface FeatureProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const Feature: React.FC<FeatureProps> = ({ icon, title, description }) => (
  <div className="flex items-start space-x-4">
    <div className="bg-white/10 p-2 rounded-full">
      {icon}
    </div>
    <div>
      <h3 className="font-semibold mb-1">{title}</h3>
      <p className="text-sm text-gray-400">
        {description}
      </p>
    </div>
  </div>
);

interface HeroSectionProps {
  description: string;
  features: {
    icon: 'chart' | 'bar' | 'bot';
    title: string;
    description: string;
  }[];
}

const HeroSection: React.FC<HeroSectionProps> = ({ description, features }) => {
  const getIcon = (iconType: string) => {
    switch (iconType) {
      case 'chart':
        return <LineChart className="h-6 w-6 text-white" />;
      case 'bar':
        return <BarChart3 className="h-6 w-6 text-white" />;
      case 'bot':
        return <Bot className="h-6 w-6 text-white" />;
      default:
        return <LineChart className="h-6 w-6 text-white" />;
    }
  };

  return (
    <div className="hidden md:flex md:w-1/2 bg-black text-white flex-col justify-center items-center p-10">
      <div className="max-w-md mx-auto">
        <h1 className="text-6xl font-bold mb-6 tracking-tight font-league-spartan">stratigo</h1>
        <p className="text-xl mb-3 text-gray-300">
          {description}
        </p>
        <p className="text-sm mb-8 text-gray-400 italic">
          A modern web application with Vue, Tailwind, and shadcn components.
        </p>
        
        <div className="space-y-6">
          {features.map((feature, index) => (
            <Feature
              key={index}
              icon={getIcon(feature.icon)}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default HeroSection; 
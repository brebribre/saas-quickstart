import React from 'react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { useToast } from '@/hooks/use-toast';

export function ToastTest() {
  const { toast: uiToast } = useToast();

  const showSonnerToast = () => {
    toast('This is a Sonner toast', {
      description: 'This is the description for the Sonner toast',
    });
  };

  const showUIToast = () => {
    uiToast({
      title: 'This is a UI toast',
      description: 'This is the description for the UI toast',
    });
  };

  return (
    <div className="flex flex-col gap-4 p-4 bg-[hsl(var(--background))] rounded-lg border border-[hsl(var(--border))]">
      <h2 className="text-xl font-bold">Toast Test</h2>
      <div className="flex gap-4">
        <Button onClick={showSonnerToast}>Show Sonner Toast</Button>
        <Button onClick={showUIToast}>Show UI Toast</Button>
      </div>
    </div>
  );
} 
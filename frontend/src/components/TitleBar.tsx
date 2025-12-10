import { Minus, Square, X } from 'lucide-react';
import * as React from "react";

// Extend Window interface to include electron API
declare global {
  interface Window {
    electron?: {
      minimize: () => void;
      maximize: () => void;
      close: () => void;
      platform: 'darwin' | 'win32' | 'linux' | 'aix' | 'freebsd' | 'openbsd' | 'sunos';
    };
  }
}

export default function TitleBar() {
  const isMac = window.electron?.platform === 'darwin';

  const handleMinimize = () => {
    window.electron?.minimize();
  };

  const handleMaximize = () => {
    window.electron?.maximize();
  };

  const handleClose = () => {
    window.electron?.close();
  };

  return (
    <div className="fixed top-0 left-0 right-0 h-12 bg-[#202225] flex items-center justify-between select-none z-50"
         style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}>

      {/* Window Controls - Only show on Windows/Linux */}
      {!isMac && (
        <div className="flex h-full" style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
          <button
            onClick={handleMinimize}
            className="w-12 h-full flex items-center justify-center hover:bg-gray-700 transition-colors"
            aria-label="Minimize"
          >
            <Minus size={16} className="text-gray-300" />
          </button>
          <button
            onClick={handleMaximize}
            className="w-12 h-full flex items-center justify-center hover:bg-gray-700 transition-colors"
            aria-label="Maximize"
          >
            <Square size={14} className="text-gray-300" />
          </button>
          <button
            onClick={handleClose}
            className="w-12 h-full flex items-center justify-center hover:bg-red-600 transition-colors"
            aria-label="Close"
          >
            <X size={16} className="text-gray-300" />
          </button>
        </div>
      )}
    </div>
  );
}

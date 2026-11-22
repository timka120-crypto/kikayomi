"use client";

import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from "react";

export interface Toast {
  id: number;
  title: string;
  description?: string;
  /** Shows an «Открыть корзину» action. */
  cartAction?: boolean;
}

interface UIContextValue {
  cartOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  toasts: Toast[];
  notify: (toast: Omit<Toast, "id">) => void;
  dismiss: (id: number) => void;
}

const UIContext = createContext<UIContextValue | null>(null);

export function UIProvider({ children }: { children: ReactNode }) {
  const [cartOpen, setCartOpen] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(1);
  const timers = useRef(new Map<number, ReturnType<typeof setTimeout>>());

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
    const timer = timers.current.get(id);
    if (timer) clearTimeout(timer);
    timers.current.delete(id);
  }, []);

  const notify = useCallback(
    (toast: Omit<Toast, "id">) => {
      const id = nextId.current++;
      // Keep at most 2 toasts on screen.
      setToasts((current) => [...current.slice(-1), { ...toast, id }]);
      timers.current.set(
        id,
        setTimeout(() => dismiss(id), 3200),
      );
    },
    [dismiss],
  );

  const value = useMemo<UIContextValue>(
    () => ({
      cartOpen,
      openCart: () => {
        // Toasts would cover the drawer header — the drawer itself shows the cart.
        setToasts([]);
        setCartOpen(true);
      },
      closeCart: () => setCartOpen(false),
      toasts,
      notify,
      dismiss,
    }),
    [cartOpen, toasts, notify, dismiss],
  );

  return <UIContext.Provider value={value}>{children}</UIContext.Provider>;
}

export function useUI(): UIContextValue {
  const context = useContext(UIContext);
  if (!context) throw new Error("useUI must be used inside <UIProvider>");
  return context;
}

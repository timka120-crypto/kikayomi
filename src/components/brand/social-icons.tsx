import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

export function InstagramIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden {...props}>
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4.2" />
      <circle cx="17.4" cy="6.6" r="1" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function TelegramIcon(props: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
      aria-hidden
      {...props}
    >
      <path d="M21.2 4.2 2.9 11.3c-.9.4-.9 1.6.1 1.9l4.6 1.4 1.8 5.5c.3.8 1.3 1 1.9.4l2.6-2.5 4.6 3.4c.7.5 1.7.1 1.9-.7L23 5.6c.2-1-.8-1.8-1.8-1.4Z" />
      <path d="m7.6 14.6 9.6-6.2-6.6 7.4" />
    </svg>
  );
}

export function WhatsAppIcon(props: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
      aria-hidden
      {...props}
    >
      <path d="M3.5 20.5 4.8 16A8.6 8.6 0 1 1 8 19.2l-4.5 1.3Z" />
      <path
        d="M9 8.3c.2-.5.5-.5.8-.5h.5c.2 0 .4 0 .6.5l.7 1.6c.1.3 0 .5-.1.7l-.5.6c-.1.2-.2.4 0 .6.5.9 1.4 1.8 2.4 2.3.2.1.4.1.6-.1l.6-.7c.2-.2.4-.3.7-.2l1.6.8c.3.1.4.3.4.5 0 .9-.6 1.7-1.5 1.9-.8.2-1.9 0-3.3-.7a9 9 0 0 1-3.6-3.6c-.8-1.4-.8-2.6-.4-3.5Z"
        fill="currentColor"
        stroke="none"
      />
    </svg>
  );
}

export const socialIcons = {
  instagram: InstagramIcon,
  telegram: TelegramIcon,
  whatsapp: WhatsAppIcon,
} as const;

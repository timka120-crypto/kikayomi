/**
 * Kazakhstan phone helpers (+7 XXX XXX XX XX). Shared by client and server.
 * All Kazakh national numbers are 10 digits and start with 7
 * (mobile 70X/747/77X, Almaty city 727, …).
 */

/** National 10 digits from any input: "+7 (701) 234-56-78" / "8 701 …" → "7012345678". */
export function phoneDigits(input: string): string {
  let digits = input.replace(/\D/g, "");
  if (digits.length > 10 && /^[78]/.test(digits)) {
    digits = digits.slice(1);
  } else if (digits.startsWith("8")) {
    // Trunk prefix typed first ("8 701 …")
    digits = digits.slice(1);
  }
  return digits.slice(0, 10);
}

/**
 * Progressive mask for the national part of the number (the "+7" prefix is
 * rendered outside the input): "701234" → "(701) 234".
 */
export function formatNationalInput(input: string): string {
  const d = phoneDigits(input);
  if (d.length === 0) return "";
  let out = "(" + d.slice(0, 3);
  if (d.length > 3) out += ") " + d.slice(3, 6);
  if (d.length > 6) out += "-" + d.slice(6, 8);
  if (d.length > 8) out += "-" + d.slice(8, 10);
  return out;
}

export function isValidPhone(input: string): boolean {
  const d = phoneDigits(input);
  return d.length === 10 && d.startsWith("7");
}

/** Canonical E.164: "+77012345678". */
export function toE164(input: string): string {
  return `+7${phoneDigits(input)}`;
}

/** Pretty print: "+7 (701) 234-56-78". */
export function formatPhone(input: string): string {
  const d = phoneDigits(input);
  if (d.length !== 10) return input;
  return `+7 (${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6, 8)}-${d.slice(8, 10)}`;
}

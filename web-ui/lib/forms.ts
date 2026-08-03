import { type FormErrors, getFormErrors, toErrorMessage } from "@/lib/api";

export const NON_FIELD_ERRORS = "non_field_errors";

/** Converts any thrown API error into a FormErrors map for display. */
export function formErrorsFromException(error: unknown): FormErrors {
  return getFormErrors(error) ?? { [NON_FIELD_ERRORS]: [toErrorMessage(error)] };
}

/** First error message for a field, or undefined. */
export function fieldError(errors: FormErrors | null, field: string): string | undefined {
  return errors?.[field]?.[0];
}

/** Errors not attributable to a specific form field. */
export function nonFieldErrors(errors: FormErrors | null, fields: string[]): string[] {
  if (!errors) {
    return [];
  }
  return Object.entries(errors)
    .filter(([key]) => !fields.includes(key))
    .flatMap(([, messages]) => messages);
}

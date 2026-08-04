import Alert from "@mui/material/Alert";
import type { FormErrors } from "@/lib/api";
import { nonFieldErrors } from "@/lib/forms";

/**
 * Form-level error messages: everything in `errors` not claimed by a
 * field the form renders itself (`fields`). Renders nothing when there
 * are none.
 */
export function FormErrorAlert({
  errors,
  fields = [],
}: {
  errors: FormErrors | null;
  fields?: string[];
}) {
  return (
    <>
      {nonFieldErrors(errors, fields).map((message) => (
        <Alert key={message} severity="error">
          {message}
        </Alert>
      ))}
    </>
  );
}

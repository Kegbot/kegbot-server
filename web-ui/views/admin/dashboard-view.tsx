import Alert from "@mui/material/Alert";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import { adminDashboardRetrieve } from "@/api-client";
import { Page } from "@/components/page";
import { unwrap } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";

function Metric({ value, caption }: { value: number; caption: string }) {
  return (
    <Grid size={{ xs: 6, sm: 4 }}>
      <Card variant="outlined" sx={{ textAlign: "center" }}>
        <CardContent>
          <Typography variant="h4">{value}</Typography>
          <Typography variant="caption" color="text.secondary">
            {caption}
          </Typography>
        </CardContent>
      </Card>
    </Grid>
  );
}

export function DashboardView() {
  const dashboard = useAsyncData(() => unwrap(adminDashboardRetrieve()));

  return (
    <Page title="Admin Dashboard" loading={dashboard.loading} error={dashboard.error}>
      {dashboard.data && (
        <Stack spacing={2}>
          {!dashboard.data.email_configured && (
            <Alert severity="warning">
              E-mail is not configured; account and notification mails will not be delivered.{" "}
              <MuiLink component={Link} to="/kegadmin/settings/advanced">
                Configure e-mail
              </MuiLink>
              .
            </Alert>
          )}
          {dashboard.data.redis_error && (
            <Alert severity="error">Redis problem: {dashboard.data.redis_error}</Alert>
          )}
          <Grid container spacing={2}>
            <Metric value={dashboard.data.num_users} caption="active drinkers" />
            <Metric value={dashboard.data.num_new_users} caption="new in the last 30 days" />
          </Grid>
        </Stack>
      )}
    </Page>
  );
}

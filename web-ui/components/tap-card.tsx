import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import type { KegTap } from "@/api-client";
import { KegProgress } from "@/components/keg-progress";
import { MONO_FONT } from "@/theme/typography";

export interface TapCardProps {
  tap: KegTap;
  /** Latest temperature at this tap, °C. */
  temperatureC?: number | null;
  temperatureLabel?: string;
  /** Kiosk sizing: larger name and gauge. */
  large?: boolean;
}

/**
 * "On tap" card. Fixed internal grid — eyebrow row, dominant beverage
 * name, one metadata line, gauge band bottom-aligned — so a row of taps
 * lines up.
 */
export function TapCard({ tap, temperatureC, temperatureLabel, large }: TapCardProps) {
  const keg = tap.current_keg;
  const beverage = keg?.beverage;
  const metadata = beverage
    ? [
        beverage.producer.name,
        beverage.style,
        beverage.abv_percent != null ? `${beverage.abv_percent}% ABV` : null,
      ]
        .filter(Boolean)
        .join(" · ")
    : "";

  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          gap: 1.5,
          p: large ? 3 : 2.5,
          "&:last-child": { pb: large ? 3 : 2.5 },
        }}
      >
        <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "baseline" }}>
          <Typography variant="overline" color="text.secondary">
            {tap.name}
          </Typography>
          {temperatureC != null && (
            <Typography
              variant="caption"
              sx={{ fontFamily: MONO_FONT, color: "text.secondary", whiteSpace: "nowrap" }}
            >
              {temperatureLabel}
            </Typography>
          )}
        </Stack>
        {keg && beverage ? (
          <>
            <Box sx={{ flexGrow: 1 }}>
              <Typography
                component="h3"
                sx={{
                  fontSize: large ? "1.875rem" : "1.375rem",
                  fontWeight: 600,
                  lineHeight: 1.2,
                  letterSpacing: "-0.01em",
                }}
              >
                <MuiLink component={Link} to={`/kegs/${keg.id}`} color="inherit" underline="hover">
                  {beverage.name}
                </MuiLink>
              </Typography>
              {metadata && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {metadata}
                </Typography>
              )}
            </Box>
            <KegProgress keg={keg} />
          </>
        ) : (
          <Box
            sx={{
              flexGrow: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              minHeight: 96,
            }}
          >
            <Typography color="text.secondary">Tap is empty.</Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

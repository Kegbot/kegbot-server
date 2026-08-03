import ThermostatIcon from "@mui/icons-material/Thermostat";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Chip from "@mui/material/Chip";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import type { KegTap } from "@/api-client";
import { KegProgress } from "@/components/keg-progress";

export interface TapCardProps {
  tap: KegTap;
  /** Latest temperature at this tap, °C. */
  temperatureC?: number | null;
  temperatureLabel?: string;
}

/** "Currently on tap" snapshot for one tap. */
export function TapCard({ tap, temperatureC, temperatureLabel }: TapCardProps) {
  const keg = tap.current_keg;
  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={1}>
          <Stack direction="row" spacing={1} sx={{ justifyContent: "space-between" }}>
            <Typography variant="overline" color="text.secondary">
              {tap.name}
            </Typography>
            {temperatureC != null && (
              <Chip
                icon={<ThermostatIcon />}
                label={temperatureLabel}
                size="small"
                variant="outlined"
              />
            )}
          </Stack>
          {keg ? (
            <>
              <Typography variant="h6">
                <MuiLink component={Link} to={`/kegs/${keg.id}`} underline="hover" color="inherit">
                  {keg.beverage.name}
                </MuiLink>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {keg.beverage.producer.name}
                {keg.beverage.style ? ` · ${keg.beverage.style}` : ""}
              </Typography>
              <KegProgress keg={keg} />
            </>
          ) : (
            <Typography color="text.secondary">Nothing on tap.</Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}

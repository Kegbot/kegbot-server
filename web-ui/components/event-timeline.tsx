import MuiLink from "@mui/material/Link";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import type { SystemEvent } from "@/api";
import { useFormatters } from "@/components/use-formatters";
import { UserLink } from "@/components/user-link";

function eventDescription(event: SystemEvent): string {
  switch (event.kind) {
    case "drink_poured":
      return "poured a drink";
    case "session_started":
      return "started a session";
    case "session_joined":
      return "joined the session";
    case "keg_tapped":
      return "keg was tapped";
    case "keg_volume_low":
      return "keg is running low";
    case "keg_ended":
      return "keg was finished";
    default:
      return event.kind;
  }
}

function EventItem({ event }: { event: SystemEvent }) {
  const { volume, relative } = useFormatters();
  const isKegEvent =
    event.kind === "keg_tapped" || event.kind === "keg_volume_low" || event.kind === "keg_ended";

  return (
    <ListItem divider disableGutters sx={{ alignItems: "flex-start" }}>
      <Stack spacing={0.5} sx={{ width: "100%" }}>
        <Stack
          direction="row"
          spacing={1}
          sx={{ alignItems: "center", justifyContent: "space-between", flexWrap: "wrap" }}
        >
          <Typography component="div" variant="body1">
            {isKegEvent && event.keg ? (
              <>
                <MuiLink component={Link} to={`/kegs/${event.keg.id}`} underline="hover">
                  {event.keg.beverage.name}
                </MuiLink>{" "}
                {eventDescription(event)}
              </>
            ) : (
              <>
                <UserLink user={event.user} /> {eventDescription(event)}
              </>
            )}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {relative(event.time)}
          </Typography>
        </Stack>
        {event.kind === "drink_poured" && event.drink && (
          <Typography variant="body2" color="text.secondary">
            <MuiLink component={Link} to={`/drinks/${event.drink.id}`} underline="hover">
              {volume(event.drink.volume_ml)}
            </MuiLink>
            {event.drink.shout ? ` — “${event.drink.shout}”` : ""}
          </Typography>
        )}
      </Stack>
    </ListItem>
  );
}

/** Feed of recent SystemEvents ("Now Drinking" timeline). */
export function EventTimeline({ events }: { events: SystemEvent[] }) {
  if (events.length === 0) {
    return <Typography color="text.secondary">No activity yet.</Typography>;
  }
  return (
    <List disablePadding>
      {events.map((event) => (
        <EventItem key={event.id} event={event} />
      ))}
    </List>
  );
}

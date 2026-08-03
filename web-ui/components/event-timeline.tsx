import SportsBarOutlinedIcon from "@mui/icons-material/SportsBarOutlined";
import Avatar from "@mui/material/Avatar";
import Box from "@mui/material/Box";
import MuiLink from "@mui/material/Link";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import type { SystemEvent } from "@/api-client";
import { EmptyState } from "@/components/empty-state";
import { useFormatters } from "@/components/use-formatters";
import { UserLink } from "@/components/user-link";
import { MONO_FONT } from "@/theme/typography";

function KegLink({ event }: { event: SystemEvent }) {
  if (!event.keg) {
    return <>A keg</>;
  }
  return (
    <MuiLink component={Link} to={`/kegs/${event.keg.id}`} underline="hover">
      {event.keg.beverage.name}
    </MuiLink>
  );
}

/** One-line sentence for an event ("alice poured 12.0 oz"). */
function EventSentence({ event }: { event: SystemEvent }) {
  const { volume } = useFormatters();

  switch (event.kind) {
    case "drink_poured":
      return (
        <>
          <UserLink user={event.user} avatarSize={0} />{" "}
          {event.drink ? (
            <>
              poured{" "}
              <MuiLink component={Link} to={`/drinks/${event.drink.id}`} underline="hover">
                {volume(event.drink.volume_ml)}
              </MuiLink>
            </>
          ) : (
            "poured a drink"
          )}
          {event.drink?.shout && (
            <Typography component="span" variant="body2" color="text.secondary">
              {" "}
              — “{event.drink.shout}”
            </Typography>
          )}
        </>
      );
    case "session_started":
      return (
        <>
          <UserLink user={event.user} avatarSize={0} /> started{" "}
          {event.session ? (
            <MuiLink component={Link} to={`/sessions/id/${event.session.id}`} underline="hover">
              a new session
            </MuiLink>
          ) : (
            "a new session"
          )}
        </>
      );
    case "session_joined":
      return (
        <>
          <UserLink user={event.user} avatarSize={0} /> joined the session
        </>
      );
    case "keg_tapped":
      return (
        <>
          <KegLink event={event} /> was tapped
        </>
      );
    case "keg_volume_low":
      return (
        <>
          <KegLink event={event} /> is running low
        </>
      );
    case "keg_ended":
      return (
        <>
          <KegLink event={event} /> was finished
        </>
      );
    default:
      return <>{event.kind}</>;
  }
}

function EventGutter({ event }: { event: SystemEvent }) {
  const isKegEvent =
    event.kind === "keg_tapped" || event.kind === "keg_volume_low" || event.kind === "keg_ended";
  if (isKegEvent || !event.user) {
    return (
      <Box
        sx={{
          width: 28,
          height: 28,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "text.secondary",
          flexShrink: 0,
        }}
      >
        <SportsBarOutlinedIcon sx={{ fontSize: 20 }} />
      </Box>
    );
  }
  const name = event.user.display_name || event.user.username;
  return (
    <Avatar
      src={event.user.picture?.thumbnail_url ?? undefined}
      sx={{ width: 28, height: 28, fontSize: "0.8125rem", flexShrink: 0 }}
    >
      {name.charAt(0).toUpperCase()}
    </Avatar>
  );
}

/** Feed of recent SystemEvents: gutter · sentence · mono time. */
export function EventTimeline({ events }: { events: SystemEvent[] }) {
  const { compactRelative } = useFormatters();
  if (events.length === 0) {
    return <EmptyState title="No activity yet." hint="Events appear as soon as beer flows." />;
  }
  return (
    <List disablePadding>
      {events.map((event) => (
        <ListItem
          key={event.id}
          divider
          disableGutters
          sx={{ py: 1.25, gap: 1.5, alignItems: "flex-start" }}
        >
          <EventGutter event={event} />
          <Typography variant="body1" sx={{ flexGrow: 1, minWidth: 0, pt: "3px" }}>
            <EventSentence event={event} />
          </Typography>
          <Typography
            variant="caption"
            sx={{
              fontFamily: MONO_FONT,
              color: "text.secondary",
              whiteSpace: "nowrap",
              pt: "6px",
            }}
          >
            {compactRelative(event.time)}
          </Typography>
        </ListItem>
      ))}
    </List>
  );
}

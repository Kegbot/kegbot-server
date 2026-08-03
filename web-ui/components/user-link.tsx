import Avatar from "@mui/material/Avatar";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link } from "react-router";
import type { User } from "@/api";

export interface UserLinkProps {
  user: User | null | undefined;
  /** Avatar size in px; 0 hides the avatar. */
  avatarSize?: number;
}

/** Avatar + username, linking to the drinker page. */
export function UserLink({ user, avatarSize = 24 }: UserLinkProps) {
  if (!user) {
    return <Typography component="span">guest</Typography>;
  }
  const name = user.display_name || user.username;
  return (
    <Stack direction="row" spacing={1} sx={{ alignItems: "center", display: "inline-flex" }}>
      {avatarSize > 0 && (
        <Avatar
          src={user.picture?.thumbnail_url ?? undefined}
          sx={{ width: avatarSize, height: avatarSize }}
        >
          {name.charAt(0).toUpperCase()}
        </Avatar>
      )}
      <MuiLink component={Link} to={`/drinkers/${user.username}`} underline="hover">
        {name}
      </MuiLink>
    </Stack>
  );
}

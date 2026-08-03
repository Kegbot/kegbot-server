import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link, useParams } from "react-router";
import { drinksPictureDestroy, drinksRetrieve } from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { useCurrentUser } from "@/components/current-user-context";
import { Page } from "@/components/page";
import { useSnackbar } from "@/components/snackbar-context";
import { useFormatters } from "@/components/use-formatters";
import { UserLink } from "@/components/user-link";
import { toErrorMessage, unwrap } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { useAsyncData } from "@/lib/use-async-data";

export function DrinkView() {
  const params = useParams();
  const drinkId = Number(params.id);
  const { volume } = useFormatters();
  const { user } = useCurrentUser();
  const confirm = useConfirm();
  const { showMessage } = useSnackbar();

  const drink = useAsyncData(() => unwrap(drinksRetrieve({ path: { id: drinkId } })), {
    deps: [drinkId],
  });

  const canManagePicture = user !== null && (user.is_staff || user.id === drink.data?.user?.id);

  const deletePicture = async () => {
    if (
      !(await confirm({
        title: "Erase this picture?",
        message: "The image will be permanently deleted.",
        confirmText: "Erase",
        destructive: true,
      }))
    ) {
      return;
    }
    try {
      await unwrap(drinksPictureDestroy({ path: { id: drinkId } }));
      showMessage("Picture erased.");
      drink.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <Page
      title={
        drink.data
          ? `${volume(drink.data.volume_ml)} of ${drink.data.keg.beverage.name}`
          : `Drink #${drinkId}`
      }
      eyebrow={`Drink #${drinkId}`}
      meta={
        drink.data && (
          <>
            poured by <UserLink user={drink.data.user} avatarSize={0} /> ·{" "}
            {formatDateTime(drink.data.time)}
            {drink.data.session_id != null && (
              <>
                {" "}
                · during{" "}
                <MuiLink
                  component={Link}
                  to={`/sessions/id/${drink.data.session_id}`}
                  underline="hover"
                >
                  session #{drink.data.session_id}
                </MuiLink>
              </>
            )}
          </>
        )
      }
      width="content"
      loading={drink.loading}
      error={drink.error}
    >
      {drink.data && (
        <Stack spacing={2.5}>
          {drink.data.shout && (
            <Typography
              variant="h5"
              component="blockquote"
              sx={{
                fontStyle: "italic",
                fontWeight: 500,
                borderLeft: 2,
                borderColor: "primary.main",
                pl: 2,
              }}
            >
              “{drink.data.shout}”
            </Typography>
          )}
          {drink.data.picture?.resized_url && (
            <Card variant="outlined" sx={{ maxWidth: 480 }}>
              <CardMedia
                component="img"
                image={drink.data.picture.resized_url}
                alt="Drink picture"
              />
              {canManagePicture && (
                <Button color="error" onClick={() => void deletePicture()} sx={{ m: 1 }}>
                  Erase picture
                </Button>
              )}
            </Card>
          )}
          <Typography variant="body2" color="text.secondary">
            Poured from{" "}
            <MuiLink component={Link} to={`/kegs/${drink.data.keg.id}`} underline="hover">
              keg #{drink.data.keg.id} — {drink.data.keg.beverage.name}
            </MuiLink>
            .
          </Typography>
        </Stack>
      )}
    </Page>
  );
}

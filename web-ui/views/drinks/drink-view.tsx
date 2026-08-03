import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link, useParams } from "react-router";
import { drinksPictureDestroy, drinksRetrieve } from "@/api";
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
    <Page title={`Drink #${drinkId}`} loading={drink.loading} error={drink.error}>
      {drink.data && (
        <Stack spacing={2}>
          <Typography>
            <UserLink user={drink.data.user} /> poured {volume(drink.data.volume_ml)} of{" "}
            <MuiLink component={Link} to={`/kegs/${drink.data.keg.id}`} underline="hover">
              {drink.data.keg.beverage.name}
            </MuiLink>{" "}
            on {formatDateTime(drink.data.time)}
            {drink.data.session_id != null && (
              <>
                {" "}
                during{" "}
                <MuiLink
                  component={Link}
                  to={`/sessions/id/${drink.data.session_id}`}
                  underline="hover"
                >
                  session #{drink.data.session_id}
                </MuiLink>
              </>
            )}
            .
          </Typography>
          {drink.data.shout && (
            <Typography variant="h6" sx={{ fontStyle: "italic" }}>
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
        </Stack>
      )}
    </Page>
  );
}

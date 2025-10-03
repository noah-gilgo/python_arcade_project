import pyglet


def update_pitch(dt, player, target_pitch, pitch_increment):
    if player.pitch < target_pitch:
        player.pitch = min(player.pitch + pitch_increment, target_pitch)


def gradually_update_pitch(player, target_pitch, pitch_increment, time_interval):
    pyglet.clock.schedule_interval(
        lambda dt: update_pitch(dt, player, target_pitch, pitch_increment),
        time_interval
    )

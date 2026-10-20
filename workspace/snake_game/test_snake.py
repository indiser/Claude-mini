"""Headless tests for the snake game logic."""

import unittest

from snake import DOWN, LEFT, RIGHT, UP, Game


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(grid=10)
        self.game.snake = [(5, 5)]
        self.game.food = (0, 0)
        self.game.direction = RIGHT
        self.game.next_direction = RIGHT

    def test_step_moves_head(self):
        self.game.step()
        self.assertEqual(self.game.snake[0], (6, 5))
        self.assertEqual(len(self.game.snake), 1)

    def test_eating_food_grows_and_scores(self):
        self.game.snake = [(4, 5)]
        self.game.food = (5, 5)
        self.game.step()
        self.assertEqual(self.game.score, 1)
        self.assertEqual(len(self.game.snake), 2)
        self.assertNotEqual(self.game.food, (5, 5))

    def test_wall_collision_ends_game(self):
        self.game.snake = [(9, 5)]
        self.game.step()
        self.assertTrue(self.game.game_over)

    def test_self_collision_ends_game(self):
        # head (5,5) moves left into the body cell (4,5)
        self.game.snake = [(5, 5), (4, 5), (4, 4), (5, 4)]
        self.game.direction = LEFT
        self.game.next_direction = LEFT
        self.game.step()
        self.assertTrue(self.game.game_over)

    def test_moving_into_tail_cell_is_allowed(self):
        # the tail moves away, so entering its cell is not a collision
        self.game.snake = [(5, 5), (5, 4), (4, 4), (4, 5)]
        self.game.direction = LEFT
        self.game.next_direction = LEFT
        self.game.step()
        self.assertFalse(self.game.game_over)

    def test_reverse_direction_is_ignored(self):
        self.game.set_direction(LEFT)
        self.assertEqual(self.game.next_direction, RIGHT)

    def test_pause_blocks_stepping(self):
        self.game.toggle_pause()
        self.game.step()
        self.assertEqual(self.game.snake[0], (5, 5))

    def test_reset_clears_state(self):
        self.game.score = 7
        self.game.game_over = True
        self.game.reset()
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_over)
        self.assertEqual(len(self.game.snake), 1)

    def test_full_board_is_a_win(self):
        self.game.grid = 2
        self.game.snake = [(1, 0), (1, 1), (0, 1)]
        self.game.food = (0, 0)
        self.game.direction = LEFT
        self.game.next_direction = LEFT
        self.assertEqual(self.game.step(), "won")
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.game_over)

    def test_directions_are_distinct(self):
        self.assertEqual(len({UP, DOWN, LEFT, RIGHT}), 4)


if __name__ == "__main__":
    unittest.main()

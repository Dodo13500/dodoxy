// ...existing code...
import java.awt.BorderLayout;
import java.awt.CardLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Rectangle;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JProgressBar;
import javax.swing.JSlider;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;

/**
 * DownloadGame - multi-level interactive Java Swing game.
 * v0.17-java — many levels, hints, simple animations, longer gameplay.
 *
 * Replace the existing DownloadGame.java with this file.
 */
public class DownloadGame extends JFrame {
    private CardLayout cards;
    private JPanel cardHolder;
    private int levelIndex = 0;
    private int score = 100;
    private JLabel scoreLabel;
    private JButton hintButton;
    private JButton nextButton;
    private JLabel levelTitle;
    private List<LevelPanel> levels;

    public DownloadGame() {
        super("DownloadGame - v0.17");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(980, 660);
        setLocationRelativeTo(null);

        initUI();
        buildLevels();
        showLevel(0);
    }

    private void initUI() {
        getContentPane().setLayout(new BorderLayout());

        // Top bar
        JPanel top = new JPanel(new BorderLayout());
        top.setBorder(new EmptyBorder(8, 12, 8, 12));
        top.setBackground(new Color(24, 28, 34));
        levelTitle = new JLabel("LEVEL");
        levelTitle.setForeground(Color.WHITE);
        levelTitle.setFont(new Font("Segoe UI", Font.BOLD, 20));
        top.add(levelTitle, BorderLayout.WEST);

        JPanel topRight = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 0));
        topRight.setOpaque(false);
        scoreLabel = new JLabel("Score: " + score);
        scoreLabel.setForeground(Color.WHITE);
        scoreLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        hintButton = new JButton("Indice (-10)");
        hintButton.setFocusable(false);
        hintButton.addActionListener(e -> useHint());
        nextButton = new JButton("Suivant ▶");
        nextButton.setEnabled(false);
        nextButton.addActionListener(e -> nextLevel());

        topRight.add(scoreLabel);
        topRight.add(hintButton);
        topRight.add(nextButton);
        top.add(topRight, BorderLayout.EAST);

        getContentPane().add(top, BorderLayout.NORTH);

        // Card holder (levels)
        cards = new CardLayout();
        cardHolder = new JPanel(cards);
        cardHolder.setBackground(new Color(18, 20, 25));
        getContentPane().add(cardHolder, BorderLayout.CENTER);

        // Bottom bar: controls
        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.CENTER, 12, 8));
        bottom.setBorder(new EmptyBorder(8, 12, 8, 12));
        bottom.setBackground(new Color(18, 20, 25));
        JButton restart = new JButton("Recommencer");
        restart.addActionListener(e -> restartGame());
        JButton exit = new JButton("Quitter");
        exit.addActionListener(e -> System.exit(0));
        bottom.add(restart);
        bottom.add(exit);
        getContentPane().add(bottom, BorderLayout.SOUTH);
    }

    private void buildLevels() {
        levels = new ArrayList<>();

        // Create a wide variety of levels with increasing complexity and animations
        levels.add(new DownloadLevel("Niveau 1 — Téléchargement tranquille", 60));
        levels.add(new ClickTargetsLevel("Niveau 2 — Cibles rapides", 12));
        levels.add(new ReactionLevel("Niveau 3 — Réaction", 1));
        levels.add(new MemoryLevel("Niveau 4 — Mémoire visuelle", 5));
        levels.add(new TypingLevel("Niveau 5 — Tape vite", 35));
        levels.add(new SliderAlignLevel("Niveau 6 — Aligne le curseur", 0.10f));
        levels.add(new WhackAMoleLevel("Niveau 7 — Tape les moles", 14));
        levels.add(new PuzzleLevel("Niveau 8 — Assemble", 3));
        levels.add(new MazeLevel("Niveau 9 — Mini labyrinthe", 1));
        levels.add(new RhythmTapLevel("Niveau 10 — Rythme", 12));
        levels.add(new SequenceMatchLevel("Niveau 11 — Suite logique", 5));
        levels.add(new DownloadLevel("Niveau 12 — Finalisation longue", 140)); // long final stage

        // Add panels to cardHolder
        for (int i = 0; i < levels.size(); i++) {
            LevelPanel lp = levels.get(i);
            cardHolder.add(lp.getPanel(), "level" + i);
        }
    }

    private void showLevel(int idx) {
        if (idx < 0 || idx >= levels.size()) return;
        levelIndex = idx;
        LevelPanel lp = levels.get(idx);
        levelTitle.setText(lp.getTitle() + "  (" + (idx + 1) + "/" + levels.size() + ")");
        scoreLabel.setText("Score: " + score);
        nextButton.setEnabled(false);
        hintButton.setEnabled(true);
        cards.show(cardHolder, "level" + idx);
        lp.start(success -> SwingUtilities.invokeLater(() -> handleLevelComplete(success)));
    }

    private void handleLevelComplete(boolean success) {
        nextButton.setEnabled(true);
        hintButton.setEnabled(false);
        if (!success) {
            score = Math.max(0, score - 5);
            scoreLabel.setText("Score: " + score);
        } else {
            score += 8;
            scoreLabel.setText("Score: " + score);
        }
    }

    private void useHint() {
        LevelPanel lp = levels.get(levelIndex);
        if (!lp.hasHint()) return;
        if (score < 10) {
            JOptionPane.showMessageDialog(this, "Pas assez de points pour un indice.", "Indice", JOptionPane.INFORMATION_MESSAGE);
            return;
        }
        score -= 10;
        scoreLabel.setText("Score: " + score);
        String hint = lp.getHint();
        JOptionPane.showMessageDialog(this, hint, "Indice", JOptionPane.INFORMATION_MESSAGE);
    }

    private void nextLevel() {
        if (levelIndex + 1 < levels.size()) {
            showLevel(levelIndex + 1);
        } else {
            JOptionPane.showMessageDialog(this, "Félicitations ! Tu as complété tous les niveaux.\nScore final: " + score, "Terminé", JOptionPane.INFORMATION_MESSAGE);
            int r = JOptionPane.showConfirmDialog(this, "Recommencer ?", "Rejouer", JOptionPane.YES_NO_OPTION);
            if (r == JOptionPane.YES_OPTION) restartGame();
        }
    }

    private void restartGame() {
        score = 100;
        scoreLabel.setText("Score: " + score);
        for (LevelPanel lp : levels) lp.reset();
        showLevel(0);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try { UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName()); } catch (Exception ignored) {}
            DownloadGame g = new DownloadGame();
            g.setVisible(true);
        });
    }

    // ---- Level infrastructure ----
    interface LevelCompleteListener { void onComplete(boolean success); }

    abstract class LevelPanel {
        protected JPanel panel;
        protected String title;
        protected boolean completed = false;
        protected LevelCompleteListener listener;

        public LevelPanel(String title) {
            this.title = title;
            panel = new JPanel(new BorderLayout());
            panel.setBackground(new Color(34, 40, 49));
            panel.setBorder(new EmptyBorder(12, 12, 12, 12));
            JLabel t = new JLabel(title);
            t.setForeground(Color.WHITE);
            t.setFont(new Font("Segoe UI", Font.BOLD, 22));
            panel.add(t, BorderLayout.NORTH);
        }

        public JPanel getPanel() { return panel; }
        public String getTitle() { return title; }
        public boolean hasHint() { return false; }
        public String getHint() { return ""; }
        public void start(LevelCompleteListener l) { this.listener = l; }
        public void reset() { completed = false; }
        protected void complete(boolean success) {
            completed = true;
            if (listener != null) listener.onComplete(success);
        }
    }

    // ---- Specific levels (with simple animations) ----

    // 1) Download simulation (longer, animated progress + bursts)
    class DownloadLevel extends LevelPanel {
        private JProgressBar bar;
        private Timer timer;
        private int speed;

        public DownloadLevel(String title, int speed) {
            super(title);
            this.speed = speed;
            bar = new JProgressBar(0, 1000);
            bar.setValue(0);
            bar.setStringPainted(true);
            bar.setForeground(new Color(70, 200, 120));
            JPanel center = new JPanel(new BorderLayout(8,8));
            center.setOpaque(false);
            center.add(bar, BorderLayout.CENTER);
            JLabel desc = new JLabel("<html><i>Simuler un long téléchargement. Patiente et observe les accélérations.</i></html>");
            desc.setForeground(Color.LIGHT_GRAY);
            center.add(desc, BorderLayout.SOUTH);
            panel.add(center, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Le téléchargement peut avoir des pics de vitesse. Reste patient."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            bar.setValue(0);
            timer = new Timer(55, null);
            timer.addActionListener(e -> {
                int v = bar.getValue();
                int inc = 1 + ThreadLocalRandom.current().nextInt(Math.max(1, speed / 40));
                // occasional burst
                if (ThreadLocalRandom.current().nextInt(200) < 8) inc += ThreadLocalRandom.current().nextInt(5, 20);
                v = Math.min(bar.getMaximum(), v + inc);
                bar.setValue(v);
                bar.setString(String.format("Téléchargement : %.1f%%", v / 10.0));
                if (v >= bar.getMaximum()) {
                    timer.stop();
                    animateCompletion();
                }
            });
            timer.start();
        }

        private void animateCompletion() {
            // small celebratory animation: flash bar color
            final Color orig = bar.getForeground();
            final Timer flash = new Timer(120, null);
            final int[] step = {0};
            flash.addActionListener(e -> {
                step[0]++;
                bar.setForeground(step[0] % 2 == 0 ? new Color(250,180,80) : orig);
                if (step[0] >= 6) {
                    flash.stop();
                    bar.setForeground(orig);
                    complete(true);
                }
            });
            flash.start();
        }

        public void reset() {
            super.reset();
            if (timer != null) timer.stop();
            bar.setValue(0);
        }
    }

    // 2) Click many targets quickly
    class ClickTargetsLevel extends LevelPanel {
        private JPanel grid;
        private int targets;
        private int clicked = 0;

        public ClickTargetsLevel(String title, int targets) {
            super(title);
            this.targets = targets;
            grid = new JPanel(new GridLayout(3, 5, 8, 8));
            grid.setOpaque(false);
            panel.add(grid, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Clique rapidement sur toutes les cibles rouges sans te tromper."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            grid.removeAll();
            clicked = 0;
            int totalCells = 15;
            Set<Integer> targetIdx = new HashSet<>();
            while (targetIdx.size() < targets) {
                targetIdx.add(ThreadLocalRandom.current().nextInt(totalCells));
            }
            for (int i = 0; i < totalCells; i++) {
                final boolean isTarget = targetIdx.contains(i);
                JButton b = new JButton();
                b.setOpaque(true);
                b.setBackground(isTarget ? new Color(220, 70, 70) : new Color(70,70,70));
                b.setFocusPainted(false);
                b.setForeground(Color.WHITE);
                b.setFont(new Font("Segoe UI", Font.PLAIN, 12));
                b.setText(isTarget ? "CIBLE" : "");
                b.addActionListener(e -> {
                    JButton src = (JButton) e.getSource();
                    if (isTarget && src.isEnabled()) {
                        src.setEnabled(false);
                        src.setBackground(new Color(100,100,100));
                        clicked++;
                        if (clicked >= targets) complete(true);
                    } else {
                        score = Math.max(0, score - 2);
                        scoreLabel.setText("Score: " + score);
                    }
                });
                grid.add(b);
            }
            grid.revalidate();
            grid.repaint();
        }

        public void reset() {
            super.reset();
            grid.removeAll();
        }
    }

    // 3) Reaction: wait for green then click
    class ReactionLevel extends LevelPanel {
        private JPanel center;
        private JButton big;
        private Timer timer;
        private boolean ready = false;

        public ReactionLevel(String title, int unused) {
            super(title);
            center = new JPanel(new GridBagLayout());
            center.setOpaque(false);
            big = new JButton("Attends...");
            big.setFont(new Font("Segoe UI", Font.BOLD, 26));
            big.setPreferredSize(new Dimension(300, 140));
            big.setBackground(new Color(130,130,130));
            big.setFocusPainted(false);
            center.add(big);
            panel.add(center, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Ne clique que lorsque le bouton devient vert."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            ready = false;
            big.setText("Attends...");
            big.setBackground(new Color(130,130,130));
            int delay = 700 + ThreadLocalRandom.current().nextInt(1400);
            timer = new Timer(delay, e -> {
                ready = true;
                big.setText("CLIQUE !");
                big.setBackground(new Color(70,200,120));
                ((Timer)e.getSource()).stop();
            });
            timer.setRepeats(false);
            timer.start();

            big.addActionListener(e -> {
                if (ready) {
                    complete(true);
                } else {
                    score = Math.max(0, score - 5);
                    scoreLabel.setText("Score: " + score);
                    if (timer != null) timer.stop();
                    // restart this level wait
                    start(listener);
                }
            });
        }

        public void reset() {
            super.reset();
            if (timer != null) timer.stop();
            ready = false;
        }
    }

    // 4) Memory sequence (flash and reproduce)
    class MemoryLevel extends LevelPanel {
        private JPanel center;
        private List<Color> seq;
        private int pos = 0;
        private JPanel buttonsPanel;

        public MemoryLevel(String title, int unused) {
            super(title);
            center = new JPanel(new BorderLayout(8,8));
            center.setOpaque(false);
            JLabel instruct = new JLabel("<html><i>Regarde la séquence et reproduis-la.</i></html>");
            instruct.setForeground(Color.LIGHT_GRAY);
            center.add(instruct, BorderLayout.NORTH);
            buttonsPanel = new JPanel(new GridLayout(1, 4, 8, 8));
            buttonsPanel.setOpaque(false);
            center.add(buttonsPanel, BorderLayout.CENTER);
            panel.add(center, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Mémorise l'ordre et reproduis-le. Les couleurs s'allument en séquence."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            seq = new ArrayList<>();
            pos = 0;
            final Color[] options = new Color[] { Color.RED, Color.BLUE, Color.GREEN, Color.ORANGE };
            buttonsPanel.removeAll();
            for (int i = 0; i < 4; i++) {
                final JButton b = new JButton();
                b.setBackground(Color.DARK_GRAY);
                b.setOpaque(true);
                b.setEnabled(false);
                b.setFocusPainted(false);
                final int idx = i;
                b.addActionListener(e -> {
                    if (b.getBackground().equals(options[idx])) {
                        pos++;
                        if (pos >= seq.size()) complete(true);
                    } else {
                        score = Math.max(0, score - 3);
                        scoreLabel.setText("Score: " + score);
                    }
                });
                buttonsPanel.add(b);
            }
            int len = 4 + ThreadLocalRandom.current().nextInt(3);
            for (int i = 0; i < len; i++) seq.add(options[ThreadLocalRandom.current().nextInt(4)]);
            playSequence(0);
        }

        private void playSequence(final int idx) {
            if (idx >= seq.size()) {
                Component[] comps = buttonsPanel.getComponents();
                for (Component c : comps) {
                    JButton b = (JButton) c;
                    b.setBackground(Color.DARK_GRAY);
                    b.setEnabled(true);
                }
                return;
            }
            final Color c = seq.get(idx);
            final int pos = ThreadLocalRandom.current().nextInt(4);
            final JButton btn = (JButton) buttonsPanel.getComponent(pos);
            final Color prev = btn.getBackground();
            btn.setBackground(c);
            Timer t = new Timer(600, e -> {
                btn.setBackground(prev);
                ((Timer)e.getSource()).stop();
                playSequence(idx + 1);
            });
            t.setRepeats(false);
            t.start();
        }

        public void reset() {
            super.reset();
            buttonsPanel.removeAll();
        }
    }

    // 5) Typing challenge
    class TypingLevel extends LevelPanel {
        private String word;
        private JTextField tf;
        private JLabel prompt;

        public TypingLevel(String title, int unused) {
            super(title);
            JPanel center = new JPanel(new BorderLayout(8,8));
            center.setOpaque(false);
            prompt = new JLabel("Tape le mot correctement :");
            prompt.setForeground(Color.LIGHT_GRAY);
            tf = new JTextField();
            tf.setFont(new Font("Consolas", Font.PLAIN, 18));
            center.add(prompt, BorderLayout.NORTH);
            center.add(tf, BorderLayout.CENTER);
            panel.add(center, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Regarde le mot affiché puis tape-le exactement."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            String[] words = {"python","download","network","pixel","rocket","tempo","mystic","archive"};
            word = words[ThreadLocalRandom.current().nextInt(words.length)];
            prompt.setText("Tape le mot :  " + word);
            tf.setText("");
            tf.requestFocusInWindow();
            tf.addActionListener(e -> {
                if (tf.getText().trim().equalsIgnoreCase(word)) {
                    complete(true);
                } else {
                    score = Math.max(0, score - 3);
                    scoreLabel.setText("Score: " + score);
                }
            });
        }

        public void reset() {
            super.reset();
            tf.setText("");
        }
    }

    // 6) Slider alignment mini-game (animated target)
    class SliderAlignLevel extends LevelPanel {
        private JSlider slider;
        private float target; // 0..1
        private JPanel bar;

        public SliderAlignLevel(String title, float tolerance) {
            super(title);
            target = ThreadLocalRandom.current().nextFloat();
            JPanel center = new JPanel(new BorderLayout());
            center.setOpaque(false);
            slider = new JSlider(0, 100, 50);
            slider.setMajorTickSpacing(25);
            JLabel info = new JLabel("Aligne le curseur le plus proche possible de la zone verte.");
            info.setForeground(Color.LIGHT_GRAY);
            center.add(info, BorderLayout.NORTH);

            bar = new JPanel() {
                protected void paintComponent(Graphics g) {
                    super.paintComponent(g);
                    int w = getWidth();
                    int h = getHeight();
                    int tx = (int) (target * w);
                    g.setColor(new Color(70, 160, 90, 200));
                    g.fillRect(Math.max(0, tx - 24), h / 4, 48, h / 2);
                    g.setColor(new Color(100,100,100));
                    g.drawRect(0, h/4, w-1, h/2);
                }
            };
            bar.setPreferredSize(new Dimension(360, 48));
            center.add(bar, BorderLayout.CENTER);
            center.add(slider, BorderLayout.SOUTH);
            panel.add(center, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Place le curseur au centre de la zone verte."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            slider.addMouseListener(new MouseAdapter() {
                public void mouseReleased(MouseEvent e) {
                    float pos = slider.getValue() / 100f;
                    if (Math.abs(pos - target) < 0.12f) {
                        complete(true);
                    } else {
                        score = Math.max(0, score - 2);
                        scoreLabel.setText("Score: " + score);
                    }
                }
            });
        }

        public void reset() {
            super.reset();
            slider.setValue(50);
            target = ThreadLocalRandom.current().nextFloat();
            bar.repaint();
        }
    }

    // 7) Whack-a-mole simplified
    class WhackAMoleLevel extends LevelPanel {
        private JPanel grid;
        private Timer moleTimer;
        private int remaining;

        public WhackAMoleLevel(String title, int targetHits) {
            super(title);
            grid = new JPanel(new GridLayout(2, 4, 8, 8));
            grid.setOpaque(false);
            panel.add(grid, BorderLayout.CENTER);
            remaining = targetHits;
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Clique rapidement sur les moles qui apparaissent."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            grid.removeAll();
            remaining = 12;
            for (int i = 0; i < 8; i++) {
                final JButton b = new JButton("");
                b.setBackground(new Color(80, 80, 80));
                b.setOpaque(true);
                b.setEnabled(true);
                b.setFocusPainted(false);
                b.addActionListener(e -> {
                    if ("MOLE".equals(b.getActionCommand())) {
                        b.setActionCommand("");
                        b.setText("");
                        b.setBackground(new Color(80, 80, 80));
                        remaining--;
                        if (remaining <= 0) complete(true);
                    } else {
                        score = Math.max(0, score - 1);
                        scoreLabel.setText("Score: " + score);
                    }
                });
                grid.add(b);
            }
            moleTimer = new Timer(650, e -> {
                Component[] comps = grid.getComponents();
                int idx = ThreadLocalRandom.current().nextInt(comps.length);
                JButton b = (JButton) comps[idx];
                b.setActionCommand("MOLE");
                b.setText("MOLE");
                b.setBackground(new Color(220, 140, 70));
                Timer t = new Timer(450, ev -> {
                    if ("MOLE".equals(b.getActionCommand())) {
                        b.setActionCommand("");
                        b.setText("");
                        b.setBackground(new Color(80, 80, 80));
                    }
                    ((Timer) ev.getSource()).stop();
                });
                t.setRepeats(false);
                t.start();
            });
            moleTimer.start();
        }

        public void reset() {
            super.reset();
            if (moleTimer != null) moleTimer.stop();
            grid.removeAll();
        }
    }

    // 8) Simple puzzle: click numbers in ascending order
    class PuzzleLevel extends LevelPanel {
        private JPanel center;
        private int steps = 0;

        public PuzzleLevel(String title, int complexity) {
            super(title);
            center = new JPanel(new GridLayout(2, 2, 8, 8));
            center.setOpaque(false);
            panel.add(center, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Clique dans l'ordre des nombres croissants."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            center.removeAll();
            List<Integer> nums = new ArrayList<>();
            for (int i = 1; i <= 4; i++) nums.add(i);
            Collections.shuffle(nums);
            steps = 0;
            for (final Integer n : nums) {
                final JButton b = new JButton(n.toString());
                b.setFont(new Font("Segoe UI", Font.BOLD, 28));
                b.addActionListener(e -> {
                    steps++;
                    b.setEnabled(false);
                    if (steps >= 4) complete(true);
                });
                center.add(b);
            }
            center.revalidate();
            center.repaint();
        }

        public void reset() {
            super.reset();
            steps = 0;
            center.removeAll();
        }
    }

    // 9) Maze level - move dot with arrow keys
    class MazeLevel extends LevelPanel {
        private MazeCanvas canvas;

        public MazeLevel(String title, int unused) {
            super(title);
            canvas = new MazeCanvas();
            panel.add(canvas, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Utilise les flèches pour atteindre la sortie."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            canvas.reset();
            canvas.requestFocusInWindow();
            canvas.setOnExit(() -> complete(true));
        }

        public void reset() {
            super.reset();
            canvas.reset();
        }

        class MazeCanvas extends JPanel {
            private int px = 20, py = 20;
            private int tile = 40;
            private int cols = 12, rows = 10;
            private Rectangle exit = new Rectangle(cols-2, rows-2,1,1);
            private Runnable onExit;

            public MazeCanvas() {
                setPreferredSize(new Dimension(cols*tile, rows*tile));
                setBackground(new Color(24,28,34));
                setFocusable(true);
                addKeyListener(new KeyAdapter() {
                    public void keyPressed(KeyEvent e) {
                        int code = e.getKeyCode();
                        if (code == KeyEvent.VK_LEFT) px = Math.max(0, px - tile);
                        if (code == KeyEvent.VK_RIGHT) px = Math.min((cols-1)*tile, px + tile);
                        if (code == KeyEvent.VK_UP) py = Math.max(0, py - tile);
                        if (code == KeyEvent.VK_DOWN) py = Math.min((rows-1)*tile, py + tile);
                        repaint();
                        if (px/tile == exit.x && py/tile == exit.y && onExit != null) onExit.run();
                    }
                });
            }

            public void reset() {
                px = tile; py = tile;
                repaint();
            }

            public void setOnExit(Runnable r) { this.onExit = r; }

            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2 = (Graphics2D) g;
                g2.setColor(new Color(50,50,50));
                for (int r=0;r<rows;r++) for (int c=0;c<cols;c++) g2.drawRect(c*tile, r*tile, tile, tile);
                // exit
                g2.setColor(new Color(70,200,120));
                g2.fillRect(exit.x*tile+4, exit.y*tile+4, tile-8, tile-8);
                // player
                g2.setColor(new Color(200,80,80));
                g2.fillOval(px+8, py+8, tile-16, tile-16);
            }
        }
    }

    // 10) Rhythm tap: press space on beats
    class RhythmTapLevel extends LevelPanel {
        private RhythmCanvas rc;

        public RhythmTapLevel(String title, int beats) {
            super(title);
            rc = new RhythmCanvas(beats);
            panel.add(rc, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Appuie sur la barre d'espace au bon moment."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            rc.start(() -> complete(true));
        }

        public void reset() {
            super.reset();
            rc.reset();
        }

        class RhythmCanvas extends JPanel {
            private int beats;
            private int beatIndex = 0;
            private Timer timer;
            private boolean lastGood = true;
            private Runnable onComplete;

            public RhythmCanvas(int beats) {
                this.beats = 8 + ThreadLocalRandom.current().nextInt(6);
                setPreferredSize(new Dimension(600,200));
                setBackground(new Color(28,30,36));
                setFocusable(true);
                addKeyListener(new KeyAdapter() {
                    public void keyPressed(KeyEvent e) {
                        if (e.getKeyCode() == KeyEvent.VK_SPACE) {
                            // evaluate timing: accept if close to beatIndex's flash
                            if (lastGood) {
                                // ok
                            } else {
                                score = Math.max(0, score - 2);
                                scoreLabel.setText("Score: " + score);
                            }
                        }
                    }
                });
            }

            public void start(Runnable onComplete) {
                this.onComplete = onComplete;
                beatIndex = 0;
                timer = new Timer(600, e -> {
                    beatIndex++;
                    lastGood = false;
                    repaint();
                    if (beatIndex >= beats) {
                        ((Timer)e.getSource()).stop();
                        if (onComplete != null) onComplete.run();
                    }
                });
                timer.start();
            }

            public void reset() {
                if (timer != null) timer.stop();
                beatIndex = 0;
            }

            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                g.setColor(Color.WHITE);
                g.drawString("Rythme : appuie Espace au bon moment", 20, 20);
                // simple animation
                int w = getWidth();
                int h = getHeight();
                int cx = (int)((double)beatIndex / Math.max(1, beats) * w);
                g.setColor(new Color(70,130,180));
                g.fillOval(cx, h/2 - 20, 40, 40);
            }
        }
    }

    // 11) Sequence match — press sequence of arrows shown
    class SequenceMatchLevel extends LevelPanel {
        private JPanel panelCenter;
        private List<Integer> seq;
        private int pos = 0;
        private JLabel info;

        public SequenceMatchLevel(String title, int length) {
            super(title);
            panelCenter = new JPanel(new BorderLayout());
            panelCenter.setOpaque(false);
            info = new JLabel("Reproduis la séquence d'arrow keys.");
            info.setForeground(Color.LIGHT_GRAY);
            panelCenter.add(info, BorderLayout.NORTH);
            panel.add(panelCenter, BorderLayout.CENTER);
        }

        public boolean hasHint() { return true; }
        public String getHint() { return "Utilise les flèches du clavier pour reproduire la séquence."; }

        public void start(LevelCompleteListener l) {
            super.start(l);
            seq = new ArrayList<>();
            pos = 0;
            int len = 4 + ThreadLocalRandom.current().nextInt(3);
            for (int i=0;i<len;i++) seq.add(ThreadLocalRandom.current().nextInt(4)); // 0..3
            showSequence(0);
            panel.setFocusable(true);
            panel.requestFocusInWindow();
            panel.addKeyListener(new KeyAdapter() {
                public void keyPressed(KeyEvent e) {
                    int code = e.getKeyCode();
                    int idx = -1;
                    if (code == KeyEvent.VK_LEFT) idx = 0;
                    if (code == KeyEvent.VK_UP) idx = 1;
                    if (code == KeyEvent.VK_RIGHT) idx = 2;
                    if (code == KeyEvent.VK_DOWN) idx = 3;
                    if (idx >= 0) {
                        if (seq.get(pos) == idx) {
                            pos++;
                            if (pos >= seq.size()) complete(true);
                        } else {
                            score = Math.max(0, score - 3);
                            scoreLabel.setText("Score: " + score);
                        }
                    }
                }
            });
        }

        private void showSequence(int i) {
            if (i >= seq.size()) {
                info.setText("A toi !");
                return;
            }
            info.setText("Regarde : " + arrowName(seq.get(i)));
            Timer t = new Timer(600, e -> {
                ((Timer)e.getSource()).stop();
                showSequence(i+1);
            });
            t.setRepeats(false);
            t.start();
        }

        private String arrowName(int v) {
            switch (v) {
                case 0: return "Gauche";
                case 1: return "Haut";
                case 2: return "Droite";
                default: return "Bas";
            }
        }

        public void reset() {
            super.reset();
            panel.removeKeyListener(panel.getKeyListeners().length>0 ? panel.getKeyListeners()[0] : new KeyAdapter(){});
        }
    }
}
// ...existing code...
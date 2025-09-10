import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.GradientPaint;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseMotionAdapter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;


/**
 * TowerDefense.java - Un jeu de Tower Defense complet et fonctionnel.
 * <p>
 * Cette version améliorée inclut :
 * - Plusieurs types de tours (Canon, Glace, Roquette, Laser, Soutien) et d'ennemis (Basique, Rapide, Tank, Volant, Guérisseur).
 * - Un système d'amélioration, de vente et de ciblage (Premier, Dernier, Fort, Faible).
 * - Des contrôles de jeu (Pause, Vitesse x1, x2, x4) et un système d'intérêts.
 * - Des effets visuels pour les tirs, les impacts et la mort des ennemis.
 * - Une interface utilisateur claire avec prévisualisation du placement des tours.
 *
 * @version 2.0
 */
public class TowerDefense extends JFrame {

    // --- Constantes du jeu ---
    public static final int TILE_SIZE = 50;
    public static final int WIDTH = 16 * TILE_SIZE; // 800
    public static final int HEIGHT = 12 * TILE_SIZE; // 600
    public static final int UI_WIDTH = 200;

    public TowerDefense() {
        super("Tower Defense");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);

        GamePanel gamePanel = new GamePanel();
        add(gamePanel);

        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(TowerDefense::new);
    }
}

class GamePanel extends JPanel implements Runnable {

    // --- État du jeu ---
    private Thread gameThread;
    private boolean running = true;
    private boolean paused = false;
    private int gameSpeed = 1;
    private int playerHealth = 100;
    private int playerMoney = 200;
    private int waveNumber = 0;

    // --- Listes d'entités ---
    private final List<Tower> towers = new ArrayList<>();
    private final List<Enemy> enemies = new ArrayList<>();
    private final List<Projectile> projectiles = new ArrayList<>();
    private final List<Projectile> newProjectiles = new ArrayList<>(); // Pour éviter ConcurrentModificationException
    private final List<VisualEffect> effects = new ArrayList<>();
    private final List<VisualEffect> newEffects = new ArrayList<>(); // Pour éviter ConcurrentModificationException
    private final List<Point> towerSpots = new ArrayList<>();
    private final List<Point> path = new ArrayList<>();

    // --- Interface utilisateur ---
    private Tower selectedTower = null;
    private String towerToBuild = "CANNON"; // Type de tour à construire
    private final Rectangle buildCannonButton = new Rectangle(TowerDefense.WIDTH + 20, 200, 160, 40);
    private final Rectangle buildFrostButton = new Rectangle(TowerDefense.WIDTH + 20, 250, 160, 40);
    private final Rectangle buildRocketButton = new Rectangle(TowerDefense.WIDTH + 20, 300, 160, 40);
    private final Rectangle buildLaserButton = new Rectangle(TowerDefense.WIDTH + 20, 350, 160, 40);
    private final Rectangle buildSupportButton = new Rectangle(TowerDefense.WIDTH + 20, 400, 160, 40);
    private final Rectangle upgradeButton = new Rectangle(TowerDefense.WIDTH + 20, 140, 160, 40);
    private final Rectangle sellButton = new Rectangle(TowerDefense.WIDTH + 20, 180, 160, 40);
    private final Rectangle targetingButton = new Rectangle(TowerDefense.WIDTH + 20, 220, 160, 40);
    private final Rectangle startWaveButton = new Rectangle(TowerDefense.WIDTH + 20, TowerDefense.HEIGHT - 60, 160, 40);
    private final Rectangle pauseButton = new Rectangle(TowerDefense.WIDTH + 20, TowerDefense.HEIGHT - 110, 75, 40);
    private final Rectangle speedButton = new Rectangle(TowerDefense.WIDTH + 105, TowerDefense.HEIGHT - 110, 75, 40);

    private Point mousePos = new Point(0, 0);
    private boolean waveInProgress = false;

    public GamePanel() {
        setPreferredSize(new Dimension(TowerDefense.WIDTH + TowerDefense.UI_WIDTH, TowerDefense.HEIGHT));
        setBackground(new Color(50, 50, 50));
        definePathAndSpots();

        addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                handleMouseClick(e.getPoint());
            }
        });

        addMouseMotionListener(new MouseMotionAdapter() {
            @Override
            public void mouseMoved(MouseEvent e) {
                mousePos = e.getPoint();
            }
        });

        startGame();
    }

    private void startGame() {
        running = true;
        gameThread = new Thread(this);
        gameThread.start();
    }

    @Override
    public void run() {
        long lastTime = System.nanoTime();
        double amountOfTicks = 60.0;
        double ns = 1000000000 / amountOfTicks;
        double delta = 0;
        final double timeStep = 1.0 / amountOfTicks;

        while (running) {
            long now = System.nanoTime();
            delta += (now - lastTime) / ns;
            lastTime = now;
            while (delta >= 1) {
                if (!paused) {
                    for (int i = 0; i < gameSpeed; i++) {
                        update(timeStep);
                    }
                }
                delta--;
            }
            repaint();
            try {
                Thread.sleep(5); // Pour ne pas surcharger le CPU
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private void update(double dt) {
        if (playerHealth <= 0) {
            gameOver();
            return;
        }

        // Mettre à jour les tours
        for (Tower tower : towers) {
            tower.update(enemies, newProjectiles, towers, newEffects, dt);
        }

        // Mettre à jour les projectiles
        Iterator<Projectile> pIt = projectiles.iterator();
        while (pIt.hasNext()) {
            Projectile p = pIt.next();
            p.update(newEffects, dt);
            if (p.hasHitTarget(enemies, newEffects)) {
                pIt.remove();
            }
        }

        // Mettre à jour les ennemis
        Iterator<Enemy> eIt = enemies.iterator();
        while (eIt.hasNext()) {
            Enemy e = eIt.next();
            // Logique de soin pour le Healer
            if (e instanceof HealerEnemy) {
                ((HealerEnemy) e).healNearby(enemies, dt);
            }
            e.update(dt);
            if (e.isDead()) {
                playerMoney += e.getBounty();
                newEffects.add(new VisualEffect(e.getCenterX(), e.getCenterY(), 20, 0.4f, new Color(255, 215, 0))); // Effet de mort
                eIt.remove();
            } else if (e.hasReachedEnd()) {
                playerHealth -= 10;
                eIt.remove();
            }
        }

        // Vérifier si la vague est terminée
        if (waveInProgress && enemies.isEmpty()) {
            waveInProgress = false;
            int interest = (int) (playerMoney * 0.05);
            playerMoney += 100 + waveNumber * 10 + interest; // Bonus de fin de vague + intérêts
        }

        // Mettre à jour les effets visuels
        Iterator<VisualEffect> vfxIt = effects.iterator();
        while (vfxIt.hasNext()) {
            VisualEffect vfx = vfxIt.next();
            if (vfx.update(dt)) vfxIt.remove();
        }

        // Ajouter les nouvelles entités créées pendant la frame
        projectiles.addAll(newProjectiles);
        effects.addAll(newEffects);
        newProjectiles.clear();
        newEffects.clear();
    }

    private void startNextWave() {
        if (waveInProgress) return;
        waveNumber++;
        waveInProgress = true;
        int enemyCount = 5 + waveNumber * 2;
        int enemyHealth = 80 + waveNumber * 20;
        float enemySpeed = 60.0f + waveNumber * 5.0f;

        for (int i = 0; i < enemyCount; i++) { // Logique de spawn améliorée
            double spawnDelay = -i * TowerDefense.TILE_SIZE * 0.7;
            if (waveNumber > 8 && i % 7 == 0) {
                enemies.add(new HealerEnemy((float) spawnDelay, path.get(0).y, path, waveNumber));
            } else if (waveNumber > 6 && i % 6 == 0) {
                enemies.add(new FlyingEnemy((float) spawnDelay, path.get(0).y, path, waveNumber));
            } else if (waveNumber > 4 && i % 5 == 0) {
                enemies.add(new TankEnemy((float) spawnDelay, path.get(0).y, path, waveNumber));
            } else if (waveNumber > 2 && i % 4 == 0) {
                enemies.add(new RunnerEnemy(-i * TowerDefense.TILE_SIZE * 0.7f, path.get(0).y, path, waveNumber));
            } else {
                enemies.add(new BasicEnemy(-i * TowerDefense.TILE_SIZE * 0.7f, path.get(0).y, enemyHealth, enemySpeed, path, waveNumber));
            }
        }
    }

    private void handleMouseClick(Point p) {
        if (!running) return;

        // Clic sur le bouton "Start Wave"
        if (startWaveButton.contains(p)) {
            if (!waveInProgress) startNextWave();
            return;
        }

        // Clics sur les boutons de contrôle du jeu
        if (pauseButton.contains(p)) {
            paused = !paused;
            return;
        }
        if (speedButton.contains(p)) {
            gameSpeed *= 2;
            if (gameSpeed > 4) {
                gameSpeed = 1;
            }
            return;
        }

        // Clic sur le bouton "Upgrade"
        if (selectedTower != null) {
            int statLines = selectedTower.getStatsString().split("\n").length;
            int upgradeButtonY = 160 + statLines * 18;
            Rectangle currentUpgradeButton = new Rectangle(upgradeButton.x, upgradeButtonY, upgradeButton.width, upgradeButton.height);
            if (currentUpgradeButton.contains(p)) {
                if (playerMoney >= selectedTower.getUpgradeCost()) {
                    playerMoney -= selectedTower.getUpgradeCost();
                    selectedTower.upgrade();
                }
                return;
            }
            // Clic sur le bouton "Sell"
            int sellButtonY = upgradeButtonY + upgradeButton.height + 10;
            Rectangle currentSellButton = new Rectangle(sellButton.x, sellButtonY, sellButton.width, sellButton.height);
            if (currentSellButton.contains(p)) {
                playerMoney += selectedTower.getSellValue();
                towers.remove(selectedTower);
                selectedTower = null;
                return;
            }
            // Clic sur le bouton "Targeting"
            int targetingButtonY = sellButtonY + sellButton.height + 10;
            Rectangle currentTargetingButton = new Rectangle(targetingButton.x, targetingButtonY, targetingButton.width, targetingButton.height);
            if (currentTargetingButton.contains(p)) {
                selectedTower.cycleTargetingMode();
                return;
            }
        }

        // Clic sur les boutons de construction
        if (buildCannonButton.contains(p)) {
            towerToBuild = "CANNON";
            selectedTower = null; // Désélectionner la tour actuelle
            return;
        }
        if (buildFrostButton.contains(p)) {
            towerToBuild = "FROST";
            selectedTower = null; // Désélectionner la tour actuelle
            return;
        }
        if (buildRocketButton.contains(p)) {
            towerToBuild = "ROCKET"; // Correction de la casse
            selectedTower = null;
            return;
        }
        if (buildLaserButton.contains(p)) {
            towerToBuild = "LASER";
            selectedTower = null;
            return;
        }
        if (buildSupportButton.contains(p)) {
            towerToBuild = "SUPPORT";
            selectedTower = null;
            return;
        }


        selectedTower = null;
        // Clic sur une tour existante
        for (Tower tower : towers) {
            if (new Rectangle(tower.x, tower.y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE).contains(p) && tower.isAlive()) {
                selectedTower = tower;
                return;
            }
        }

        // Clic sur un emplacement de tour vide
        for (Point spot : towerSpots) {
            Rectangle spotRect = new Rectangle(spot.x, spot.y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
            if (spotRect.contains(p)) {
                boolean isOccupied = towers.stream().anyMatch(t -> t.x == spot.x && t.y == spot.y);
                if (!isOccupied) {
                    if ("CANNON".equals(towerToBuild) && playerMoney >= CannonTower.BASE_COST) {
                        playerMoney -= CannonTower.BASE_COST;
                        towers.add(new CannonTower(spot.x, spot.y));
                    } else if ("FROST".equals(towerToBuild) && playerMoney >= FrostTower.BASE_COST) {
                        playerMoney -= FrostTower.BASE_COST;
                        towers.add(new FrostTower(spot.x, spot.y));
                    } else if ("ROCKET".equals(towerToBuild) && playerMoney >= RocketTower.BASE_COST) {
                        playerMoney -= RocketTower.BASE_COST;
                        towers.add(new RocketTower(spot.x, spot.y));
                    } else if ("LASER".equals(towerToBuild) && playerMoney >= LaserTower.BASE_COST) {
                        playerMoney -= LaserTower.BASE_COST;
                        towers.add(new LaserTower(spot.x, spot.y));
                    } else if ("SUPPORT".equals(towerToBuild) && playerMoney >= SupportTower.BASE_COST) {
                        playerMoney -= SupportTower.BASE_COST;
                        towers.add(new SupportTower(spot.x, spot.y));
                    }
                }
                return;
            }
        }
    }

    private void gameOver() {
        running = false;
    }

    private void drawTowerPreview(Graphics2D g2d) {
        int gridX = mousePos.x / TowerDefense.TILE_SIZE;
        int gridY = mousePos.y / TowerDefense.TILE_SIZE;
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Dessiner le fond
        // Dégradé pour le fond
        GradientPaint gp = new GradientPaint(0, 0, new Color(40, 80, 40), 0, TowerDefense.HEIGHT, new Color(20, 60, 20));
        g2d.setPaint(gp);
        g2d.fillRect(0, 0, TowerDefense.WIDTH, TowerDefense.HEIGHT); // Vert plus foncé

        // Dessiner le chemin
        // Bordure du chemin
        g2d.setColor(new Color(119, 105, 87)); // Marron plus foncé
        g2d.setStroke(new BasicStroke(TowerDefense.TILE_SIZE, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        for (int i = 0; i < path.size() - 1; i++) {
            Point p1 = path.get(i);
            Point p2 = path.get(i + 1);
            g2d.drawLine(p1.x, p1.y, p2.x, p2.y);
        }
        // Chemin intérieur
        g2d.setColor(new Color(189, 165, 127)); // Beige
        g2d.setStroke(new BasicStroke(TowerDefense.TILE_SIZE - 10, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        for (int i = 0; i < path.size() - 1; i++) {
            g2d.drawLine(path.get(i).x, path.get(i).y, path.get(i + 1).x, path.get(i + 1).y);
        }

        // Dessiner les effets visuels (explosions, etc.)
        // Copie de la liste pour éviter ConcurrentModificationException
        List<VisualEffect> effectsCopy = new ArrayList<>(effects);
        for (VisualEffect vfx : effectsCopy) {
            vfx.draw(g2d);
        }
        // Dessiner les emplacements de tour
        g2d.setColor(new Color(0, 100, 0, 100));
        for (Point spot : towerSpots) {
            g2d.fillRect(spot.x, spot.y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
        }

        // Dessiner les tours
        for (Tower tower : towers) {
            if (tower.isAlive()) tower.draw(g2d);
            if (tower == selectedTower) {
                g2d.setColor(new Color(255, 255, 0, 100));
                g2d.drawOval(tower.x + TowerDefense.TILE_SIZE / 2 - tower.getRange(), tower.y + TowerDefense.TILE_SIZE / 2 - tower.getRange(), tower.getRange() * 2, tower.getRange() * 2);
            }
        }

        // Dessiner la prévisualisation de la tour
        if (towerToBuild != null && mousePos.x < TowerDefense.WIDTH) {
            int gridX = mousePos.x / TowerDefense.TILE_SIZE;
            int gridY = mousePos.y / TowerDefense.TILE_SIZE;
            int x = gridX * TowerDefense.TILE_SIZE;
            int y = gridY * TowerDefense.TILE_SIZE;

            boolean isSpot = towerSpots.stream().anyMatch(p -> p.x == x && p.y == y);
            boolean isOccupied = towers.stream().anyMatch(t -> t.x == x && t.y == y);

            if (isSpot && !isOccupied) {
                g2d.setColor(new Color(0, 255, 0, 100)); // Vert pour valide
            } else {
                g2d.setColor(new Color(255, 0, 0, 100)); // Rouge pour invalide
            }
            g2d.fillRect(x, y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);

            // Dessiner la portée de la tour en prévisualisation (amélioré)
            int previewRange = 0;
            if ("CANNON".equals(towerToBuild)) previewRange = CannonTower.INITIAL_RANGE;
            else if ("FROST".equals(towerToBuild)) previewRange = FrostTower.INITIAL_RANGE;
            else if ("ROCKET".equals(towerToBuild)) previewRange = RocketTower.INITIAL_RANGE;
            else if ("LASER".equals(towerToBuild)) previewRange = LaserTower.INITIAL_RANGE;
            else if ("SUPPORT".equals(towerToBuild)) previewRange = SupportTower.INITIAL_RANGE;

            if (previewRange > 0) {
                g2d.setColor(new Color(255, 255, 255, 70));
                g2d.drawOval(x + TowerDefense.TILE_SIZE / 2 - previewRange, y + TowerDefense.TILE_SIZE / 2 - previewRange, previewRange * 2, previewRange * 2);
            }
        }
        // Dessiner les ennemis
        for (Enemy enemy : enemies) {
            enemy.draw(g2d);
        }

        // Dessiner les projectiles
        for (Projectile p : projectiles) {
            p.draw(g2d);
        }

        // Dessiner l'interface utilisateur
        drawUI(g2d);

        if (!running && playerHealth <= 0) {
            g2d.setColor(new Color(0, 0, 0, 150));
            g2d.fillRect(0, 0, TowerDefense.WIDTH, TowerDefense.HEIGHT);
            g2d.setColor(Color.RED);
            g2d.setFont(new Font("Arial", Font.BOLD, 80));
            String msg = "GAME OVER";
            int w = g2d.getFontMetrics().stringWidth(msg);
            g2d.drawString(msg, TowerDefense.WIDTH / 2 - w / 2, TowerDefense.HEIGHT / 2);
        }

        if (paused) {
            g2d.setColor(new Color(0, 0, 0, 100));
            g2d.fillRect(0, 0, TowerDefense.WIDTH, TowerDefense.HEIGHT);
            g2d.setColor(Color.YELLOW);
            g2d.setFont(new Font("Arial", Font.BOLD, 50));
            g2d.drawString("PAUSE", TowerDefense.WIDTH / 2 - 100, TowerDefense.HEIGHT / 2);
        }
    }

    private void drawUI(Graphics2D g2d) {
        g2d.setColor(new Color(45, 45, 45)); // Gris foncé
        g2d.fillRect(TowerDefense.WIDTH, 0, TowerDefense.UI_WIDTH, TowerDefense.HEIGHT);

        g2d.setColor(Color.WHITE);
        g2d.setFont(new Font("Arial", Font.BOLD, 20));

        g2d.drawString("❤️ Vie: " + playerHealth, TowerDefense.WIDTH + 20, 40);
        g2d.drawString("Argent: " + playerMoney + "$", TowerDefense.WIDTH + 20, 70);
        g2d.drawString("Vague: " + waveNumber, TowerDefense.WIDTH + 20, 100);

        // Panneau de la tour sélectionnée
        if (selectedTower != null) {
            g2d.drawString(selectedTower.getName() + " Niv. " + selectedTower.getLevel(), TowerDefense.WIDTH + 20, 130);

            // Affichage des stats
            g2d.setFont(new Font("Arial", Font.PLAIN, 14));
            int statY = 160;
            for (String statLine : selectedTower.getStatsString().split("\n")) {
                g2d.drawString(statLine, TowerDefense.WIDTH + 20, statY);
                statY += 18;
            }

            // Bouton Améliorer
            g2d.setColor(new Color(80, 200, 80));
            g2d.fill(new Rectangle(upgradeButton.x, statY, upgradeButton.width, upgradeButton.height));
            g2d.setColor(Color.BLACK);
            g2d.setFont(new Font("Arial", Font.BOLD, 16));
            String upgradeText = "Améliorer (" + selectedTower.getUpgradeCost() + "$)";
            int w = g2d.getFontMetrics().stringWidth(upgradeText);
            g2d.drawString(upgradeText, upgradeButton.x + (upgradeButton.width - w) / 2, statY + 25);

            // Bouton Vendre
            int sellButtonY = statY + upgradeButton.height + 10;
            g2d.setColor(new Color(220, 80, 80));
            g2d.fill(new Rectangle(sellButton.x, sellButtonY, sellButton.width, sellButton.height));
            g2d.setColor(Color.BLACK);
            g2d.drawString("Vendre (" + selectedTower.getSellValue() + "$)", sellButton.x + 35, sellButtonY + 25);

            // Bouton de Ciblage
            int targetingButtonY = sellButtonY + sellButton.height + 20; // Plus d'espace
            g2d.setColor(new Color(150, 150, 255));
            g2d.fill(new Rectangle(targetingButton.x, targetingButtonY, targetingButton.width, targetingButton.height));
            g2d.setColor(Color.BLACK);
            g2d.drawString("Cible: " + selectedTower.getTargetingModeName(), targetingButton.x + 20, targetingButtonY + 25);
        } else { // Panneau de construction si aucune tour n'est sélectionnée
            // Panneau de construction
            g2d.setFont(new Font("Arial", Font.BOLD, 20));
            g2d.setColor(Color.CYAN);
            g2d.drawString("Construire:", TowerDefense.WIDTH + 20, 190);

            // Bouton Cannon
            g2d.setColor(towerToBuild.equals("CANNON") ? Color.ORANGE : Color.LIGHT_GRAY);
            g2d.fill(buildCannonButton);
            g2d.setColor(Color.BLACK);
            g2d.setFont(new Font("Arial", Font.BOLD, 16));
            String cannonText = "Canon (" + CannonTower.BASE_COST + "$)";
            int w = g2d.getFontMetrics().stringWidth(cannonText);
            g2d.drawString(cannonText, buildCannonButton.x + (buildCannonButton.width - w) / 2, buildCannonButton.y + 25);

            // Bouton Frost
            g2d.setColor(towerToBuild.equals("FROST") ? Color.ORANGE : Color.LIGHT_GRAY);
            g2d.fill(buildFrostButton);
            g2d.setColor(Color.BLACK);
            String frostText = "Glace (" + FrostTower.BASE_COST + "$)";
            w = g2d.getFontMetrics().stringWidth(frostText);
            g2d.drawString(frostText, buildFrostButton.x + (buildFrostButton.width - w) / 2, buildFrostButton.y + 25);

            // Bouton Rocket
            g2d.setColor(towerToBuild.equals("ROCKET") ? Color.ORANGE : Color.LIGHT_GRAY);
            g2d.fill(buildRocketButton);
            g2d.setColor(Color.BLACK);
            String rocketText = "Roquette (" + RocketTower.BASE_COST + "$)";
            w = g2d.getFontMetrics().stringWidth(rocketText);
            g2d.drawString(rocketText, buildRocketButton.x + (buildRocketButton.width - w) / 2, buildRocketButton.y + 25);

            // Bouton Laser
            g2d.setColor(towerToBuild.equals("LASER") ? Color.ORANGE : Color.LIGHT_GRAY);
            g2d.fill(buildLaserButton);
            g2d.setColor(Color.BLACK);
            String laserText = "Laser (" + LaserTower.BASE_COST + "$)";
            w = g2d.getFontMetrics().stringWidth(laserText);
            g2d.drawString(laserText, buildLaserButton.x + (buildLaserButton.width - w) / 2, buildLaserButton.y + 25);

            // Bouton Support
            g2d.setColor(towerToBuild.equals("SUPPORT") ? Color.ORANGE : Color.LIGHT_GRAY);
            g2d.fill(buildSupportButton);
            g2d.setColor(Color.BLACK);
            String supportText = "Support (" + SupportTower.BASE_COST + "$)";
            w = g2d.getFontMetrics().stringWidth(supportText);
            g2d.drawString(supportText, buildSupportButton.x + (buildSupportButton.width - w) / 2, buildSupportButton.y + 25);
        }

        // Bouton de vague
        g2d.setColor(waveInProgress ? Color.GRAY : Color.CYAN);
        g2d.fill(startWaveButton);
        g2d.setColor(Color.BLACK);
        g2d.setFont(new Font("Segoe UI", Font.BOLD, 16));
        String waveText = "Vague " + (waveNumber + 1);
        int w = g2d.getFontMetrics().stringWidth(waveText);
        g2d.drawString(waveText, startWaveButton.x + (startWaveButton.width - w) / 2, startWaveButton.y + 25);

        // Boutons de contrôle du jeu
        g2d.setColor(paused ? Color.YELLOW : Color.LIGHT_GRAY);
        g2d.fill(pauseButton);
        g2d.setColor(Color.BLACK);
        // Dessiner manuellement les symboles pour éviter les problèmes de police
        if (paused) { // Dessiner le symbole Play (▶)
            int[] xPoints = {pauseButton.x + 28, pauseButton.x + 28, pauseButton.x + 48};
            int[] yPoints = {pauseButton.y + 10, pauseButton.y + 30, pauseButton.y + 20};
            g2d.fillPolygon(xPoints, yPoints, 3);
        } else { // Dessiner le symbole Pause (❚❚)
            g2d.fillRect(pauseButton.x + 28, pauseButton.y + 10, 8, 20);
            g2d.fillRect(pauseButton.x + 42, pauseButton.y + 10, 8, 20);
        }

        g2d.setColor(Color.LIGHT_GRAY);
        g2d.fill(speedButton);
        g2d.setColor(Color.BLACK);
        g2d.drawString("x" + gameSpeed, speedButton.x + 30, speedButton.y + 25);
    }

    private void definePathAndSpots() {
        // Définir le chemin que les ennemis suivront (coordonnées des centres des tuiles)
        path.add(new Point(-TowerDefense.TILE_SIZE / 2, 3 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2));
        path.add(new Point(4 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2, 3 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2));
        path.add(new Point(4 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2, 8 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2));
        path.add(new Point(12 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2, 8 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2));
        path.add(new Point(12 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2, 2 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2));
        path.add(new Point(TowerDefense.WIDTH + TowerDefense.TILE_SIZE / 2, 2 * TowerDefense.TILE_SIZE + TowerDefense.TILE_SIZE / 2));

        // Définir les emplacements où les tours peuvent être construites
        towerSpots.add(new Point(2 * TowerDefense.TILE_SIZE, 1 * TowerDefense.TILE_SIZE));
        towerSpots.add(new Point(2 * TowerDefense.TILE_SIZE, 4 * TowerDefense.TILE_SIZE));
        towerSpots.add(new Point(6 * TowerDefense.TILE_SIZE, 3 * TowerDefense.TILE_SIZE));
        towerSpots.add(new Point(6 * TowerDefense.TILE_SIZE, 6 * TowerDefense.TILE_SIZE));
        towerSpots.add(new Point(10 * TowerDefense.TILE_SIZE, 9 * TowerDefense.TILE_SIZE));
        towerSpots.add(new Point(10 * TowerDefense.TILE_SIZE, 5 * TowerDefense.TILE_SIZE));
        towerSpots.add(new Point(10 * TowerDefense.TILE_SIZE, 0 * TowerDefense.TILE_SIZE));
        towerSpots.add(new Point(14 * TowerDefense.TILE_SIZE, 3 * TowerDefense.TILE_SIZE));
    }
}

abstract class Tower {
    enum TargetingMode { FIRST, LAST, STRONGEST, WEAKEST }

    protected int x, y, range, damage, level;
    protected float fireRate; // Tirs par seconde
    protected float baseFireRate; // Pour les buffs
    protected long lastFireTime;
    protected int cost, upgradeCost;
    protected Enemy target;
    protected TargetingMode targetingMode = TargetingMode.FIRST;
    protected long totalDamageDealt = 0;
    protected double cannonAngle = 0;

    public Tower(int x, int y, int range, int damage, float fireRate, int cost, int upgradeCost) {
        this.x = x;
        this.y = y;
        this.range = range;
        this.damage = damage;
        this.fireRate = fireRate;
        this.baseFireRate = fireRate;
        this.cost = cost;
        this.upgradeCost = upgradeCost;
        this.level = 1;
        this.lastFireTime = 0;
        this.cost = cost; // S'assurer que le coût initial est stocké
    }

    public void update(List<Enemy> enemies, List<Projectile> newProjectiles, List<Tower> allTowers, List<VisualEffect> newEffects, double dt) {
        fireRate = baseFireRate; // Reset pour les buffs
        findTarget(enemies);
        if (target != null) {
            cannonAngle = Math.atan2(target.getCenterY() - (y + TowerDefense.TILE_SIZE / 2), target.getCenterX() - (x + TowerDefense.TILE_SIZE / 2));
            long currentTime = System.nanoTime();
            if ((currentTime - lastFireTime) / 1_000_000_000.0 >= 1.0 / fireRate) {
                fire(newProjectiles, newEffects);
                lastFireTime = currentTime;
            }
        }
    }

    public void applyBuff(float fireRateMultiplier) {
        this.fireRate = this.baseFireRate * fireRateMultiplier;
    }

    private void findTarget(List<Enemy> enemies) {
        if (target != null && (target.isDead() || distanceTo(target) > range)) {
            target = null;
        }

        if (target == null) {
            List<Enemy> potentialTargets = new ArrayList<>();
            for (Enemy e : enemies) { // Filtre les cibles valides
                if (canTarget(e) && distanceTo(e) <= range) {
                    potentialTargets.add(e);
                }
            }

            if (potentialTargets.isEmpty()) return;

            switch (targetingMode) {
                case FIRST:
                    target = potentialTargets.stream().max(Comparator.comparing(Enemy::getPathIndex)).orElse(null);
                    break;
                case LAST:
                    target = potentialTargets.stream().min(Comparator.comparing(Enemy::getPathIndex)).orElse(null);
                    break;
                case STRONGEST:
                    target = potentialTargets.stream().max(Comparator.comparing(Enemy::getHealth)).orElse(null);
                    break;
                case WEAKEST:
                    target = potentialTargets.stream().min(Comparator.comparing(Enemy::getHealth)).orElse(null);
                    break;
            }
        }
    }

    public void cycleTargetingMode() {
        targetingMode = TargetingMode.values()[(targetingMode.ordinal() + 1) % TargetingMode.values().length];
    }

    public String getTargetingModeName() {
        switch (targetingMode) {
            case FIRST: return "Premier";
            case LAST: return "Dernier";
            case STRONGEST: return "Plus Fort";
            case WEAKEST: return "Plus Faible";
            default: return "";
        }
    }

    protected double distanceToTower(Tower t) {
        int dx = (t.x + TowerDefense.TILE_SIZE / 2) - (this.x + TowerDefense.TILE_SIZE / 2);
        int dy = (t.y + TowerDefense.TILE_SIZE / 2) - (this.y + TowerDefense.TILE_SIZE / 2);
        return Math.sqrt(dx * dx + dy * dy);
    }

    private double distanceTo(Enemy e) {
        int dx = e.getCenterX() - (this.x + TowerDefense.TILE_SIZE / 2);
        int dy = e.getCenterY() - (this.y + TowerDefense.TILE_SIZE / 2);
        return Math.sqrt(dx * dx + dy * dy);
    }

    public abstract void fire(List<Projectile> newProjectiles, List<VisualEffect> newEffects);
    public abstract void draw(Graphics2D g2d);
    public abstract void upgrade();
    public abstract String getName();
    public abstract boolean canTarget(Enemy e);
    public abstract String getStatsString();

    public int getDamage() { return damage; }
    public float getFireRate() { return fireRate; }
    public int getRange() { return range; }
    public int getLevel() { return level; }
    public int getUpgradeCost() { return upgradeCost; }
    public int getSellValue() {
        return (int) ((cost + (upgradeCost - getBaseUpgradeCost()) / 0.5 * 0.5) * 0.75);
    }
    public abstract int getBaseUpgradeCost();
    public boolean isAlive() { return true; } // Pour la compatibilité avec la logique de vente
}

class CannonTower extends Tower {
    public static final int BASE_COST = 100;
    public static final int INITIAL_RANGE = 120;

    public CannonTower(int x, int y) {
        super(x, y, INITIAL_RANGE, 25, 1.0f, BASE_COST, 75);
    }

    @Override
    public void fire(List<Projectile> newProjectiles, List<VisualEffect> newEffects) {
        Bullet b = new Bullet(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2, damage, target);
        b.setSource(this);
        newProjectiles.add(b);
        newEffects.add(new VisualEffect(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2, 8, 0.1f, Color.YELLOW)); // Muzzle flash
    }

    @Override
    public boolean canTarget(Enemy e) { return true; } // Le canon peut tout cibler

    @Override
    public void draw(Graphics2D g2d) {
        // Base circulaire
        g2d.setColor(new Color(80, 80, 80));
        g2d.fillOval(x + 5, y + 5, TowerDefense.TILE_SIZE - 10, TowerDefense.TILE_SIZE - 10);
        g2d.setColor(Color.DARK_GRAY);
        g2d.drawOval(x + 5, y + 5, TowerDefense.TILE_SIZE - 10, TowerDefense.TILE_SIZE - 10);

        // Canon
        Graphics2D g2d_rotated = (Graphics2D) g2d.create();
        g2d_rotated.translate(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2);
        g2d_rotated.rotate(cannonAngle);
        g2d_rotated.setColor(new Color(50, 50, 50));
        g2d_rotated.fillRect(10, -5, 25, 10);
        g2d_rotated.setColor(Color.BLACK);
        g2d_rotated.drawRect(10, -5, 25, 10);
        g2d_rotated.dispose();
    }

    @Override
    public void upgrade() {
        this.level++;
        this.damage += 15;
        this.range += 10;
        this.baseFireRate *= 1.1f;
        this.upgradeCost = (int) (this.upgradeCost * 1.5);
    }

    @Override
    public String getName() {
        return "Canon";
    }

    @Override
    public String getStatsString() {
        return String.format("Dégâts: %d\nPortée: %d\nCadence: %.1f/s\nDégâts totaux: %d", damage, range, fireRate, totalDamageDealt);
    }

    @Override
    public int getBaseUpgradeCost() { return 75; }
}

class FrostTower extends Tower {
    public static final int BASE_COST = 150;
    public static final int INITIAL_RANGE = 100;
    private int slowDuration = 120; // 2 seconds at 60fps

    public FrostTower(int x, int y) {
        super(x, y, INITIAL_RANGE, 0, 0.8f, BASE_COST, 120);
    }

    @Override
    public void fire(List<Projectile> newProjectiles, List<VisualEffect> newEffects) {
        FrostBolt fb = new FrostBolt(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2, slowDuration, target);
        fb.setSource(this);
        newProjectiles.add(fb);
        newEffects.add(new VisualEffect(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2, 10, 0.15f, Color.CYAN));
    }

    @Override
    public boolean canTarget(Enemy e) { return !e.isFlying; } // Ne peut pas cibler les volants

    @Override
    public void draw(Graphics2D g2d) {
        // Base
        g2d.setColor(new Color(60, 120, 160));
        g2d.fillOval(x + 5, y + 5, TowerDefense.TILE_SIZE - 10, TowerDefense.TILE_SIZE - 10);
        // Cristal
        g2d.setColor(Color.CYAN);
        int[] xPoints = {x + 25, x + 10, x + 25, x + 40};
        int[] yPoints = {y + 10, y + 25, y + 40, y + 25};
        g2d.fillPolygon(xPoints, yPoints, 4);
    }

    @Override
    public void upgrade() {
        this.level++;
        this.range += 15;
        this.slowDuration += 30; // 0.5s
        this.upgradeCost = (int) (this.upgradeCost * 1.6);
    }

    @Override
    public String getName() {
        return "Tour de Glace";
    }

    @Override
    public String getStatsString() {
        return String.format("Ralentissement: %.1fs\nPortée: %d\nCadence: %.1f/s\nDégâts totaux: %d", slowDuration / 60.0, range, fireRate, totalDamageDealt);
    }

    @Override
    public int getBaseUpgradeCost() { return 120; }
}

class RocketTower extends Tower {
    public static final int BASE_COST = 250;
    public static final int INITIAL_RANGE = 180;

    public RocketTower(int x, int y) {
        // Dégâts de zone, cadence lente, longue portée
        super(x, y, INITIAL_RANGE, 40, 0.5f, BASE_COST, 200);
    }

    @Override
    public void fire(List<Projectile> newProjectiles, List<VisualEffect> newEffects) {
        Rocket r = new Rocket(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2, damage, target);
        r.setSource(this);
        newProjectiles.add(r);
        newEffects.add(new VisualEffect(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2, 12, 0.2f, Color.ORANGE));
    }

    @Override
    public boolean canTarget(Enemy e) { return true; } // Peut tout cibler

    @Override
    public void draw(Graphics2D g2d) {
        // Base
        g2d.setColor(new Color(70, 70, 70));
        g2d.fillRect(x + 5, y + 5, TowerDefense.TILE_SIZE - 10, TowerDefense.TILE_SIZE - 10);
        g2d.setColor(Color.BLACK);
        g2d.drawRect(x + 5, y + 5, TowerDefense.TILE_SIZE - 10, TowerDefense.TILE_SIZE - 10);

        // Lance-roquettes
        Graphics2D g2d_rotated = (Graphics2D) g2d.create();
        g2d_rotated.translate(x + TowerDefense.TILE_SIZE / 2, y + TowerDefense.TILE_SIZE / 2);
        g2d_rotated.rotate(cannonAngle);
        g2d_rotated.setColor(new Color(100, 0, 0));
        g2d_rotated.fillRect(0, -8, 25, 16);
        g2d_rotated.setColor(Color.BLACK);
        g2d_rotated.drawRect(0, -8, 25, 16);
        g2d_rotated.dispose();
    }

    @Override
    public void upgrade() {
        this.level++;
        this.damage += 25; // Augmente les dégâts de l'explosion
        this.range += 20;
        this.upgradeCost = (int) (this.upgradeCost * 1.8);
    }

    @Override
    public String getName() { return "Lance-Roquettes"; }

    @Override
    public String getStatsString() {
        return String.format("Dégâts (zone): %d\nPortée: %d\nCadence: %.1f/s\nDégâts totaux: %d", damage, range, fireRate, totalDamageDealt);
    }

    @Override
    public int getBaseUpgradeCost() { return 200; }
}

class LaserTower extends Tower {
    public static final int BASE_COST = 300;
    public static final int INITIAL_RANGE = 150;

    public LaserTower(int x, int y) {
        super(x, y, INITIAL_RANGE, 5, 10.0f, BASE_COST, 250); // Dégâts par tick, cadence très élevée
    }

    @Override
    public void fire(List<Projectile> newProjectiles, List<VisualEffect> newEffects) {
        // Le laser n'utilise pas de projectiles, il inflige des dégâts directement
        if (target != null) {
            target.takeDamage(damage);
            totalDamageDealt += damage;
            newEffects.add(new VisualEffect(target.getCenterX(), target.getCenterY(), 5, 0.05f, Color.RED)); // Corrected
        }
    }

    @Override
    public void draw(Graphics2D g2d) {
        g2d.setColor(new Color(50, 0, 100));
        g2d.fillRect(x + 5, y + 5, TowerDefense.TILE_SIZE - 10, TowerDefense.TILE_SIZE - 10);
        g2d.setColor(Color.MAGENTA);
        g2d.fillOval(x + 15, y + 15, TowerDefense.TILE_SIZE - 30, TowerDefense.TILE_SIZE - 30);
        if (target != null && !target.isDead()) {
            g2d.setStroke(new BasicStroke(3));
            g2d.setColor(new Color(255, 0, 255, 150));
            g2d.drawLine(x + 25, y + 25, target.getCenterX(), target.getCenterY());
            g2d.setStroke(new BasicStroke(1));
        }
    }

    @Override
    public void upgrade() {
        level++;
        damage += 3;
        range += 15;
        upgradeCost *= 1.7;
    }

    @Override
    public String getName() { return "Tour Laser"; }

    @Override
    public boolean canTarget(Enemy e) { return true; }

    @Override
    public String getStatsString() {
        return String.format("Dégâts/tick: %d\nPortée: %d\nCadence: %.1f/s\nDégâts totaux: %d", damage, range, fireRate, totalDamageDealt);
    }

    @Override
    public int getBaseUpgradeCost() { return 250; }
}

class SupportTower extends Tower {
    public static final int BASE_COST = 200;
    public static final int INITIAL_RANGE = 100;
    private float fireRateBuff = 1.25f; // 25% de cadence en plus

    public SupportTower(int x, int y) {
        super(x, y, INITIAL_RANGE, 0, 0, BASE_COST, 180);
    }

    @Override
    public void update(List<Enemy> enemies, List<Projectile> newProjectiles, List<Tower> allTowers, List<VisualEffect> newEffects, double dt) {
        // N'attaque pas, mais buff les tours proches
        for (Tower t : allTowers) {
            if (t != this && distanceToTower(t) <= range) {
                t.applyBuff(fireRateBuff);
            }
        }
        // Effet visuel d'aura
        newEffects.add(new VisualEffect(x + 25, y + 25, (int)(range * (0.8 + 0.2 * Math.sin(System.currentTimeMillis() / 200.0))), 0.1f, new Color(255, 255, 100, 50)));
    }

    @Override
    public void fire(List<Projectile> newProjectiles, List<VisualEffect> newEffects) {
        // Ne tire pas
    }

    @Override
    public void draw(Graphics2D g2d) {
        g2d.setColor(new Color(200, 200, 100));
        g2d.fillRect(x + 5, y + 5, TowerDefense.TILE_SIZE - 10, TowerDefense.TILE_SIZE - 10);
        g2d.setColor(Color.WHITE);
        g2d.setStroke(new BasicStroke(4));
        g2d.drawLine(x + 15, y + 25, x + 35, y + 25); // Horizontal
        g2d.drawLine(x + 25, y + 15, x + 25, y + 35); // Vertical
        g2d.setStroke(new BasicStroke(1));
    }

    @Override
    public void upgrade() {
        level++;
        range += 10;
        fireRateBuff += 0.1f;
        upgradeCost *= 1.6;
    }

    @Override
    public String getName() { return "Tour de Soutien"; }

    @Override
    public boolean canTarget(Enemy e) { return false; }

    @Override
    public String getStatsString() {
        return String.format("Buff Cadence: +%.0f%%\nPortée: %d", (fireRateBuff - 1) * 100, range);
    }

    @Override
    public int getBaseUpgradeCost() { return 180; }
}

abstract class Enemy {
    protected float x, y;
    protected int health;
    protected int maxHealth;
    protected float speed;
    protected float originalSpeed;
    protected int pathIndex = 1; // Commence à viser le 2ème point
    protected int bounty;
    protected List<Point> path;

    protected boolean isSlowed = false;
    protected int slowTicksRemaining = 0;

    public Enemy(float x, float y, int health, float speed, int bounty, List<Point> path, int wave) {
        this.x = x;
        this.y = y - TowerDefense.TILE_SIZE / 2f; // Centrer sur l'axe Y du chemin
        this.health = health;
        this.maxHealth = health;
        this.speed = speed;
        this.originalSpeed = speed;
        this.bounty = bounty;
        this.path = path;
    }
    public boolean isFlying = false;

    public void update(double dt) {
        if (isSlowed) {
            slowTicksRemaining--;
            if (slowTicksRemaining <= 0) {
                isSlowed = false;
                speed = originalSpeed;
            }
        }

        if (pathIndex >= path.size() || isDead()) return;

        Point targetPoint = path.get(pathIndex);

        double angle = Math.atan2(targetPoint.y - getCenterY(), targetPoint.x - getCenterX());
        x += speed * Math.cos(angle) * dt;
        y += speed * Math.sin(angle) * dt;

        double distToTarget = Math.sqrt(Math.pow(targetPoint.x - getCenterX(), 2) + Math.pow(targetPoint.y - getCenterY(), 2));
        if (distToTarget < speed * dt) {
            pathIndex++;
        }
    }

    public void draw(Graphics2D g2d) {
        // Corps de l'ennemi
        drawBody(g2d);

        if (isFlying) { // Ombre pour les ennemis volants
            g2d.setColor(new Color(0, 0, 0, 70));
            g2d.fillOval((int) x + 5, (int) y + 5, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
        }

        if (isSlowed) {
            g2d.setColor(new Color(0, 150, 255, 100));
            g2d.fillOval((int) x, (int) y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
        }

        // Barre de vie
        g2d.setColor(Color.DARK_GRAY);
        g2d.fillRect((int) x, (int) y - 10, TowerDefense.TILE_SIZE, 5);
        g2d.setColor(Color.GREEN);
        g2d.fillRect((int) x, (int) y - 10, (int) (TowerDefense.TILE_SIZE * ((double) health / maxHealth)), 5);
    }

    public void takeDamage(int amount) {
        this.health -= amount;
    }

    public void applySlow(int durationTicks) {
        if (!isSlowed) {
            isSlowed = true;
            speed = originalSpeed / 2;
        }
        slowTicksRemaining = durationTicks;
    }

    public boolean isDead() { return health <= 0; }
    public boolean hasReachedEnd() { return pathIndex >= path.size(); }
    public int getX() { return (int) x; }
    public int getY() { return (int) y; }
    public int getCenterX() { return (int) (x + TowerDefense.TILE_SIZE / 2); }
    public int getCenterY() { return (int) (y + TowerDefense.TILE_SIZE / 2); }
    public int getBounty() { return bounty; }
    public abstract Color getBodyColor();
    public abstract void drawBody(Graphics2D g2d);
    public int getPathIndex() { return pathIndex; }
    public int getHealth() { return health; }
}

class BasicEnemy extends Enemy {
    public BasicEnemy(float x, float y, int health, float speed, List<Point> path, int wave) {
        super(x, y, health, speed, 10, path, wave);
    }

    @Override
    public Color getBodyColor() {
        return Color.RED;
    }

    @Override
    public void drawBody(Graphics2D g2d) {
        g2d.setColor(getBodyColor());
        g2d.fillOval((int) x, (int) y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
    }
}

class RunnerEnemy extends Enemy {
    public RunnerEnemy(float x, float y, List<Point> path, int wave) {
        super(x, y, 60 + wave * 8, 150.0f, 15, path, wave); // Moins de vie, plus de vitesse
    }

    @Override
    public Color getBodyColor() {
        return new Color(255, 165, 0); // Orange
    }

    @Override
    public void drawBody(Graphics2D g2d) {
        g2d.setColor(getBodyColor());
        int[] xPoints = {(int)x + 25, (int)x, (int)x + 50};
        int[] yPoints = {(int)y, (int)y + 50, (int)y + 50};
        g2d.fillPolygon(xPoints, yPoints, 3);
    }
}

class TankEnemy extends Enemy {
    public TankEnemy(float x, float y, List<Point> path, int wave) {
        super(x, y, 500 + wave * 40, 30.0f, 50, path, wave); // Très résistant, lent
    }

    @Override
    public Color getBodyColor() {
        return new Color(128, 0, 128); // Purple
    }

    @Override
    public void drawBody(Graphics2D g2d) {
        g2d.setColor(getBodyColor());
        g2d.fillRect((int) x, (int) y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
    }
}

class FlyingEnemy extends Enemy {
    public FlyingEnemy(float x, float y, List<Point> path, int wave) {
        super(x, y, 75 + wave * 10, 108.0f, 20, path, wave);
        this.isFlying = true;
    }

    @Override
    public Color getBodyColor() {
        return Color.WHITE;
    }

    @Override
    public void drawBody(Graphics2D g2d) {
        g2d.setColor(getBodyColor());
        // Corps
        g2d.fillOval((int)x + 10, (int)y + 10, 30, 30);
        // Ailes
        g2d.fillOval((int)x, (int)y + 15, 20, 20);
        g2d.fillOval((int)x + 30, (int)y + 15, 20, 20);
    }
}

class HealerEnemy extends Enemy {
    private long lastHealTime = 0;
    private final int healRadius = 60;
    private final int healAmount = 2;
    private double healCooldown = 1.0; // en secondes

    public HealerEnemy(float x, float y, List<Point> path, int wave) {
        super(x, y, 150 + wave * 20, 60.0f, 40, path, wave);
    }

    public void healNearby(List<Enemy> allEnemies, double dt) {
        healCooldown -= dt;
        if (healCooldown <= 0) {
            for (Enemy e : allEnemies) {
                if (e != this && !e.isDead() && Math.hypot(e.getCenterX() - getCenterX(), e.getCenterY() - getCenterY()) <= healRadius) {
                    e.health = Math.min(e.maxHealth, e.health + healAmount);
                }
            }
            healCooldown = 1.0; // Réinitialiser le cooldown
        }
    }

    @Override
    public Color getBodyColor() {
        return new Color(46, 204, 113); // Vert émeraude
    }

    @Override
    public void drawBody(Graphics2D g2d) {
        g2d.setColor(getBodyColor());
        g2d.fillOval((int) x, (int) y, TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
        g2d.setColor(Color.WHITE);
        g2d.fillRect((int)x + 20, (int)y + 10, 10, 30);
        g2d.fillRect((int)x + 10, (int)y + 20, 30, 10);
    }
}

abstract class Projectile {
    protected float x, y;
    protected final Enemy target;
    protected float speed = 480.0f; // pixels par seconde
    protected Tower source; // La tour qui a tiré

    public Projectile(float x, float y, Enemy target) {
        this.x = x;
        this.y = y;
        this.target = target;
    }

    public void setSource(Tower source) {
        this.source = source;
    }

    public void update(List<VisualEffect> newEffects, double dt) {
        if (target == null || target.isDead()) return;
        int targetX = target.getCenterX(), targetY = target.getCenterY();
        
        double angle = Math.atan2(targetY - y, targetX - x);
        x += speed * Math.cos(angle) * dt;
        y += speed * Math.sin(angle) * dt;
    }

    public boolean hasHitTarget(List<Enemy> allEnemies, List<VisualEffect> effects) {
        if (target == null || target.isDead()) return true;
        Rectangle projRect = new Rectangle((int) x - 3, (int) y - 3, 6, 6);
        Rectangle enemyRect = new Rectangle(target.getX(), target.getY(), TowerDefense.TILE_SIZE, TowerDefense.TILE_SIZE);
        if (projRect.intersects(enemyRect)) {
            onHit(allEnemies, effects);
            return true;
        }
        return false;
    }

    public abstract void onHit(List<Enemy> allEnemies, List<VisualEffect> effects);
    public abstract void draw(Graphics2D g2d);
}

class Bullet extends Projectile {
    private final int damage;

    public Bullet(float x, float y, int damage, Enemy target) {
        super(x, y, target);
        this.damage = damage;
    }

    @Override
    public void onHit(List<Enemy> allEnemies, List<VisualEffect> effects) {
        target.takeDamage(damage);
        if (source != null) source.totalDamageDealt += damage;
    }

    @Override
    public void draw(Graphics2D g2d) {
        g2d.setColor(Color.YELLOW);
        g2d.fillOval((int) x - 4, (int) y - 4, 8, 8);
    }
}

class FrostBolt extends Projectile {
    private final int slowDuration;

    public FrostBolt(float x, float y, int slowDuration, Enemy target) {
        super(x, y, target);
        this.slowDuration = slowDuration;
        this.speed = 360.0f;
    }

    @Override
    public void onHit(List<Enemy> allEnemies, List<VisualEffect> effects) {
        target.applySlow(slowDuration);
        // Les projectiles de glace ne font pas de dégâts par défaut
    }

    @Override
    public void draw(Graphics2D g2d) {
        g2d.setColor(Color.CYAN);
        g2d.fillRect((int) x - 4, (int) y - 4, 8, 8);
    }
}

class Rocket extends Projectile {
    private final int damage;
    private final int splashRadius = 40; // Rayon de l'explosion

    public Rocket(float x, float y, int damage, Enemy target) {
        super(x, y, target);
        this.damage = damage;
        this.speed = 240.0f; // Les roquettes sont plus lentes
    }

    @Override
    public void update(List<VisualEffect> newEffects, double dt) {
        super.update(newEffects, dt);
        // Ajoute une traînée de fumée
        newEffects.add(new VisualEffect((int)x, (int)y, 4, 0.2f, new Color(128, 128, 128, 150)));
    }

    @Override
    public void onHit(List<Enemy> allEnemies, List<VisualEffect> newEffects) {
        if (newEffects != null) {
            newEffects.add(new VisualEffect(target.getCenterX(), target.getCenterY(), splashRadius, 0.3f, new Color(255, 165, 0)));
        }
        // Appliquer des dégâts de zone
        for (Enemy e : allEnemies) {
            if (!e.isDead()) {
                double dist = Math.sqrt(Math.pow(e.getCenterX() - target.getCenterX(), 2) + Math.pow(e.getCenterY() - target.getCenterY(), 2));
                if (dist <= splashRadius) {
                    int damageDealt = Math.min(e.health, damage);
                    e.takeDamage(damage);
                    if (source != null) source.totalDamageDealt += damageDealt;
                }
            }
        }
    }

    @Override
    public void draw(Graphics2D g2d) {
        g2d.setColor(Color.ORANGE);
        g2d.fillOval((int) x - 6, (int) y - 6, 12, 12);
        g2d.setColor(Color.RED);
        g2d.fillOval((int) x - 2, (int) y - 2, 4, 4);
    }
}

class VisualEffect {
    float x, y, radius, life, maxLife; // life en secondes
    Color color;

    public VisualEffect(float x, float y, int radius, float life, Color color) {
        this.x = x; this.y = y; this.radius = radius; this.life = life; this.maxLife = life; this.color = color;
    }

    public boolean update(double dt) {
        life -= dt;
        return life <= 0;
    }

    public void draw(Graphics2D g2d) {
        float alpha = Math.max(0, life / maxLife); // Utilise maxLife pour un fondu correct
        g2d.setColor(new Color(color.getRed(), color.getGreen(), color.getBlue(), (int) (alpha * 255)));
        int currentRadius = (int) (radius * (1.0f - alpha));
        g2d.fillOval((int)(x - currentRadius), (int)(y - currentRadius), currentRadius * 2, currentRadius * 2);
    }
}
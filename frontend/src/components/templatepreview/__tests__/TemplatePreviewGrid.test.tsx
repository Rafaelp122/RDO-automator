import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TemplatePreviewGrid } from '../TemplatePreviewGrid';
import type { TemplateSheet } from '../../../types';

function makeSheet(overrides: Partial<TemplateSheet> = {}): TemplateSheet {
  return {
    name: 'Sheet1',
    cells: [],
    images: [],
    merged: [],
    colWidths: null,
    rowHeights: null,
    ...overrides,
  };
}

function makeCell(
  coord: string,
  row: number,
  col: number,
  value: string | null = null,
  style: Record<string, string> | null = null,
) {
  return { coord, row, col, value, font: null, style };
}

describe('TemplatePreviewGrid', () => {
  describe('empty state', () => {
    it('shows placeholder when no sheets', () => {
      render(<TemplatePreviewGrid sheets={[]} />);
      expect(screen.getByText('Carregue um template para visualizar')).toBeInTheDocument();
    });
  });

  describe('cell rendering', () => {
    it('renders cell values', () => {
      const sheet = makeSheet({
        cells: [
          makeCell('A1', 1, 1, 'Header'),
          makeCell('B1', 1, 2, 'Value'),
        ],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      expect(screen.getByText('Header')).toBeInTheDocument();
      expect(screen.getByText('Value')).toBeInTheDocument();
    });

    it('renders empty cell for null value', () => {
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, null)],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      const headers = screen.getAllByText('A');
      expect(headers.length).toBeGreaterThan(0);
    });
  });

  describe('inline styles', () => {
    it('applies style prop to td', () => {
      const sheet = makeSheet({
        cells: [
          makeCell('A1', 1, 1, 'Styled', {
            'background-color': '#FFFF00',
            'font-weight': 'bold',
            'color': '#FF0000',
          }),
        ],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      const cell = screen.getByText('Styled').closest('td');
      expect(cell).toBeInTheDocument();
      expect(cell!.style.backgroundColor).toBe('rgb(255, 255, 0)');
      expect(cell!.style.fontWeight).toBe('bold');
      expect(cell!.style.color).toBe('rgb(255, 0, 0)');
    });
  });

  describe('merged cells', () => {
    it('applies colspan to merged cell anchor', () => {
      const sheet = makeSheet({
        cells: [
          makeCell('A1', 1, 1, 'MergedHeader'),
          makeCell('B1', 1, 2, null),
          makeCell('C1', 1, 3, null),
        ],
        merged: [{ min_col: 1, max_col: 3, min_row: 1, max_row: 1 }],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      const cell = screen.getByText('MergedHeader').closest('td');
      expect(cell).toBeInTheDocument();
      expect((cell as HTMLElement).colSpan).toBe(3);
    });

    it('hides non-anchor cells in merged range', () => {
      const sheet = makeSheet({
        cells: [
          makeCell('A1', 1, 1, 'Anchor'),
          makeCell('B1', 1, 2, 'ShouldBeHidden'),
        ],
        merged: [{ min_col: 1, max_col: 2, min_row: 1, max_row: 1 }],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      expect(screen.getByText('Anchor')).toBeInTheDocument();
      expect(screen.queryByText('ShouldBeHidden')).not.toBeInTheDocument();
    });

    it('handles multi-row merged ranges', () => {
      const sheet = makeSheet({
        cells: [
          makeCell('A1', 1, 1, 'TallCell'),
          makeCell('A2', 2, 1, 'HiddenRow2'),
          makeCell('A3', 3, 1, 'HiddenRow3'),
        ],
        merged: [{ min_col: 1, max_col: 1, min_row: 1, max_row: 3 }],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      const cell = screen.getByText('TallCell').closest('td');
      expect(cell).toBeInTheDocument();
      expect(cell!.getAttribute('rowspan')).toBe('3');
      expect(screen.queryByText('HiddenRow2')).not.toBeInTheDocument();
      expect(screen.queryByText('HiddenRow3')).not.toBeInTheDocument();
    });

    it('does not crash with empty merged array', () => {
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, 'Normal')],
        merged: [],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      expect(screen.getByText('Normal')).toBeInTheDocument();
    });
  });

  describe('column widths and row heights', () => {
    it('applies column widths via colgroup', () => {
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, 'Data')],
        colWidths: { A: 15, B: 20 },
      });
      const { container } = render(<TemplatePreviewGrid sheets={[sheet]} />);
      const cols = container.querySelectorAll('col');
      const dataCols = Array.from(cols).filter(
        (c) => c.style.width !== '32px',
      );
      expect(dataCols.length).toBeGreaterThanOrEqual(1);
    });

    it('does not crash with null colWidths', () => {
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, 'Data')],
        colWidths: null,
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      expect(screen.getByText('Data')).toBeInTheDocument();
    });
  });

  describe('interactive mode', () => {
    it('calls onCellClick when clicking empty cell in interactive mode', () => {
      const onClick = vi.fn();
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, null)],
      });
      const { container } = render(
        <TemplatePreviewGrid
          sheets={[sheet]}
          onCellClick={onClick}
        />,
      );
      const td = container.querySelector('td.cursor-pointer');
      expect(td).not.toBeNull();
      fireEvent.click(td!);
      expect(onClick).toHaveBeenCalledWith('A1');
    });

    it('does not call onCellClick on cells with values', () => {
      const onClick = vi.fn();
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, 'HasValue')],
      });
      render(
        <TemplatePreviewGrid
          sheets={[sheet]}
          onCellClick={onClick}
        />,
      );
      fireEvent.click(screen.getByText('HasValue').closest('td')!);
      expect(onClick).not.toHaveBeenCalled();
    });
  });

  describe('images', () => {
    it('renders images as img elements', () => {
      const sheet = makeSheet({
        cells: [],
        images: [
          {
            b64: 'data:image/png;base64,test',
            position: { col: 1, row: 0, colOff: 0, rowOff: 0 },
          },
        ],
      });
      const { container } = render(
        <TemplatePreviewGrid sheets={[sheet]} />,
      );
      const imgs = container.querySelectorAll('img');
      expect(imgs.length).toBe(1);
      expect(imgs[0].getAttribute('src')).toBe('data:image/png;base64,test');
    });

    it('skips images with missing position', () => {
      const sheet = makeSheet({
        cells: [],
        images: [
          {
            b64: 'data:image/png;base64,test',
            position: {},
          },
        ],
      });
      const { container } = render(
        <TemplatePreviewGrid sheets={[sheet]} />,
      );
      const imgs = container.querySelectorAll('img');
      expect(imgs.length).toBe(0);
    });

    it('does not crash with no images', () => {
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, 'Data')],
        images: [],
      });
      render(<TemplatePreviewGrid sheets={[sheet]} />);
      expect(screen.getByText('Data')).toBeInTheDocument();
    });
  });

  describe('mapped cells', () => {
    it('shows mapping badge on empty cell', () => {
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, null)],
      });
      const mappedCells = {
        A1: {
          id: 'map-1',
          sourceColumns: ['Col1'],
          templateCell: 'A1',
          formatTemplate: 'Test Format',
        },
      };
      render(
        <TemplatePreviewGrid
          sheets={[sheet]}
          mappedCells={mappedCells}
        />,
      );
      expect(screen.getByText('Test Format')).toBeInTheDocument();
    });
  });

  describe('selected cell', () => {
    it('applies selection ring to selected cell', () => {
      const sheet = makeSheet({
        cells: [makeCell('A1', 1, 1, null)],
      });
      const { container } = render(
        <TemplatePreviewGrid
          sheets={[sheet]}
          selectedCell="A1"
        />,
      );
      const td = container.querySelector('.ring-2');
      expect(td).toBeInTheDocument();
    });
  });
});

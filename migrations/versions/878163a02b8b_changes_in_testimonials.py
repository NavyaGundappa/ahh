"""Changes in Testimonials

Revision ID: 878163a02b8b
Revises: c1717c5dfc30
Create Date: 2025-11-15 09:54:41.829758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '878163a02b8b'
down_revision = 'c1717c5dfc30'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('testimonial', schema=None) as batch_op:

        # Step 1: Add columns as nullable=True first
        batch_op.add_column(
            sa.Column('patient_name', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('content', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('patient_image_path',
                            sa.String(length=300), nullable=True))
        batch_op.add_column(
            sa.Column('doctor_id', sa.Integer(), nullable=True))

        # Step 2: Drop old columns
        batch_op.drop_column('image_path')
        batch_op.drop_column('alt_text')

    # Step 3: Fill default values so NOT NULL will not fail
    op.execute(
        "UPDATE testimonial SET patient_name = 'Unknown' WHERE patient_name IS NULL")
    op.execute(
        "UPDATE testimonial SET content = 'No content provided' WHERE content IS NULL")

    # Step 4: Now enforce NOT NULL safely
    with op.batch_alter_table('testimonial', schema=None) as batch_op:
        batch_op.alter_column('patient_name', nullable=False)
        batch_op.alter_column('content', nullable=False)

        # Step 5: Create named foreign key
        batch_op.create_foreign_key(
            'fk_testimonial_doctor_id',
            'doctors',
            ['doctor_id'],
            ['id']
        )


def downgrade():
    with op.batch_alter_table('testimonial', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_testimonial_doctor_id', type_='foreignkey')

        batch_op.add_column(
            sa.Column('alt_text', sa.VARCHAR(length=200), nullable=True))
        batch_op.add_column(
            sa.Column('image_path', sa.VARCHAR(length=300), nullable=False))

        batch_op.drop_column('doctor_id')
        batch_op.drop_column('patient_image_path')
        batch_op.drop_column('content')
        batch_op.drop_column('patient_name')
